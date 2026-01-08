import numpy as np
import pandas as pd
from typing import Tuple, Optional
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AIModel:
    """AI/ML model for trading signals"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        
    def prepare_training_data(self, features: pd.DataFrame, 
                             labels: pd.Series) -> Tuple:
        """Prepare data for training"""
        # Handle missing values
        features = features.fillna(method='ffill').fillna(0)
        
        # Remove outliers
        for col in features.columns:
            q1 = features[col].quantile(0.25)
            q3 = features[col].quantile(0.75)
            iqr = q3 - q1
            features = features[
                (features[col] >= q1 - 1.5 * iqr) & 
                (features[col] <= q3 + 1.5 * iqr)
            ]
        
        # Align labels with filtered features
        labels = labels.loc[features.index]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test, scaler
    
    def train_model(self, features: pd.DataFrame, labels: pd.Series,
                   model_type: str = 'gradient_boosting') -> dict:
        """
        Train AI model
        
        Returns:
            Dict with model, scaler, and metrics
        """
        logger.info(f"Training {model_type} model...")
        
        # Prepare data
        X_train, X_test, y_train, y_test, scaler = self.prepare_training_data(
            features, labels
        )
        
        # Train model
        if model_type == 'random_forest':
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model accuracy: {accuracy:.2%}")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        return {
            'model': model,
            'scaler': scaler,
            'accuracy': accuracy,
            'features': features.columns.tolist()
        }
    
    def predict(self, features: pd.DataFrame, model, scaler) -> Tuple[str, float]:
        """
        Make prediction using trained model
        
        Returns:
            Tuple of (signal, confidence)
        """
        try:
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Get prediction probabilities
            probabilities = model.predict_proba(features_scaled)[0]
            
            # Get predicted class
            predicted_class = model.predict(features_scaled)[0]
            
            # Map to signals
            class_to_signal = {
                0: 'SELL',
                1: 'NEUTRAL', 
                2: 'BUY'
            }
            
            signal = class_to_signal.get(predicted_class, 'NEUTRAL')
            confidence = max(probabilities)
            
            # Adjust confidence based on probability distribution
            if signal != 'NEUTRAL' and confidence > 0.6:
                # High confidence in directional signal
                return signal, confidence
            else:
                # Low confidence or neutral signal
                return 'NEUTRAL', confidence
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 'NEUTRAL', 0.0
    
    def generate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate features from raw market data"""
        features = pd.DataFrame()
        
        # Price-based features
        features['returns_1'] = data['close'].pct_change(1)
        features['returns_5'] = data['close'].pct_change(5)
        features['returns_20'] = data['close'].pct_change(20)
        
        # Volatility features
        features['volatility_5'] = features['returns_1'].rolling(5).std()
        features['volatility_20'] = features['returns_1'].rolling(20).std()
        
        # Volume features
        features['volume_ratio'] = data['volume'] / data['volume'].rolling(20).mean()
        features['volume_std'] = data['volume'].rolling(20).std() / data['volume'].rolling(20).mean()
        
        # Price position features
        rolling_high = data['high'].rolling(20).max()
        rolling_low = data['low'].rolling(20).min()
        features['price_position'] = (data['close'] - rolling_low) / (rolling_high - rolling_low + 1e-10)
        
        # Momentum features
        features['momentum_5'] = data['close'] / data['close'].shift(5) - 1
        features['momentum_20'] = data['close'] / data['close'].shift(20) - 1
        
        # Drop NaN values
        features = features.dropna()
        
        return features
    
    def generate_labels(self, data: pd.DataFrame, 
                       forward_period: int = 3) -> pd.Series:
        """
        Generate labels for supervised learning
        
        Labels: 0 = SELL, 1 = NEUTRAL, 2 = BUY
        """
        # Calculate future returns
        future_returns = data['close'].shift(-forward_period) / data['close'] - 1
        
        # Create labels based on future returns
        labels = pd.Series(1, index=data.index)  # Default: NEUTRAL
        
        # BUY if future return > threshold
        buy_threshold = 0.01  # 1%
        sell_threshold = -0.01  # -1%
        
        labels[future_returns > buy_threshold] = 2  # BUY
        labels[future_returns < sell_threshold] = 0  # SELL
        
        # Align with features (remove last forward_period rows)
        labels = labels.iloc[:-forward_period]
        
        return labels
