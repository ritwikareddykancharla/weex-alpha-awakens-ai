import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from src.utils.logger import setup_logger
import joblib
import os

logger = setup_logger(__name__)

class RegimeClassifier:
    """
    Classifies market regimes using Gaussian Mixture Models (GMM).
    Regimes:
    0: Calm / Range-bound (Low Vol, Neutral Funding)
    1: Trending (Moderate Vol, Directional Funding)
    2: High Volatility / Crash / Squeeze (High Vol, Extreme Funding)
    """
    def __init__(self, n_components=3, model_path="models/regime_gmm.pkl"):
        self.n_components = n_components
        self.model_path = model_path
        self.model = GaussianMixture(n_components=n_components, covariance_type='full', random_state=42)
        self.is_fitted = False
        
        # Load if exists
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.is_fitted = True
                logger.info("Loaded existing Regime GMM model.")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from OHLCV + Funding Data.
        Expected columns: ['close', 'high', 'low', 'fundingRate', 'openInterest']
        """
        df = df.copy()
        
        # 1. Volatility (Parkinson or simple Std Dev of returns)
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(24*365) # Annualized-ish or just raw
        
        # 2. Funding Rate Volatility/Magnitude
        # Funding rate often comes as string or float. Ensure float.
        if 'fundingRate' not in df.columns:
            df['fundingRate'] = 0.0 # Default if missing
        
        df['funding_mag'] = df['fundingRate'].abs()
        
        # 3. Open Interest Change (if available)
        if 'openInterest' in df.columns:
            df['oi_change'] = df['openInterest'].pct_change()
        else:
            df['oi_change'] = 0.0
            
        # Drop NaNs
        features = df[['volatility', 'funding_mag', 'oi_change']].dropna()
        return features

    def fit(self, df: pd.DataFrame):
        """Train the GMM on historical data"""
        features = self.prepare_features(df)
        if len(features) < 50:
            logger.warning("Not enough data to fit Regime Classifier")
            return
            
        self.model.fit(features)
        self.is_fitted = True
        logger.info("Regime Classifier fitted successfully.")
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def predict(self, df: pd.DataFrame) -> int:
        """Predict regime for the *latest* data point"""
        if not self.is_fitted:
            logger.warning("Model not fitted, returning default regime 0")
            return 0
            
        features = self.prepare_features(df)
        if features.empty:
            return 0
            
        # Predict on specific latest slice or valid tail
        latest_features = features.iloc[[-1]] 
        regime = self.model.predict(latest_features)[0]
        probs = self.model.predict_proba(latest_features)[0]
        
        logger.info(f"Detected Regime: {regime} (Prob: {probs[regime]:.2f})")
        return regime
