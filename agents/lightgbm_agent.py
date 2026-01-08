import lightgbm as lgb
import pandas as pd
import numpy as np
import logging
import joblib

class LightGBMAgent:
    def __init__(self, model_path="data/lgbm_model.pkl"):
        self.model = None
        self.model_path = model_path
        self.features = [] # List of feature names
        
        # Hyperparameters (Optimized for Crypto Noise)
        self.params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }

    def train_live(self, kline_data):
        """
        Takes raw OHLCV data, creates features, and retrains the model.
        kline_data: List of [time, open, high, low, close, volume...]
        """
        # 1. Feature Engineering (The "Secret Sauce")
        df = self._prepare_features(kline_data)
        
        # 2. Create Target (Did price go UP 1% in next 3 candles?)
        # We look 3 periods (45 mins) ahead
        future_close = df['close'].shift(-3)
        df['target'] = (future_close > df['close'] * 1.005).astype(int)
        
        # Drop NaNs created by shifts
        df.dropna(inplace=True)
        
        if len(df) < 100:
            return 0.0 # Not enough data
            
        X = df[self.features]
        y = df['target']
        
        # 3. Train
        train_data = lgb.Dataset(X, label=y)
        self.model = lgb.train(self.params, train_data, num_boost_round=100)
        
        # Save for persistence
        joblib.dump(self.model, self.model_path)
        return self.model.best_score.get('auc', 0)

    def predict(self, kline_data):
        if not self.model:
            return 0, 0.0
            
        # Prepare just the LAST row for prediction
        df = self._prepare_features(kline_data)
        last_row = df.iloc[[-1]][self.features]
        
        # Predict Probability
        prob = self.model.predict(last_row)[0]
        
        # Signal Logic
        signal = 0
        if prob > 0.65: signal = 1  # BUY
        elif prob < 0.35: signal = -1 # SELL
        
        return signal, prob

    def _prepare_features(self, data):
        """
        Converts raw candles into a tabular format LightGBM understands.
        """
        df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'a', 'b'])
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # --- FEATURE ENGINEERING ---
        
        # 1. Returns (Momentum)
        for lag in [1, 3, 6, 12]: # 15m, 45m, 1.5h, 3h
            df[f'return_lag_{lag}'] = df['close'].pct_change(lag)
            
        # 2. Volatility (Rolling Std Dev)
        df['volatility_20'] = df['close'].rolling(20).std() / df['close']
        
        # 3. Volume Spikes
        df['vol_ma_20'] = df['volume'].rolling(20).mean()
        df['vol_ratio'] = df['volume'] / (df['vol_ma_20'] + 1e-8)
        
        # 4. RSI (Relative Strength) - Vectorized
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Save feature names for later use
        self.features = [c for c in df.columns if c not in ['time', 'open', 'high', 'low', 'close', 'target', 'a', 'b']]
        
        return df

    def get_rationale(self):
        """
        Returns the top features that drove the decision (For AI Log)
        """
        if not self.model: return "Model not trained"
        
        importance = self.model.feature_importance(importance_type='gain')
        feature_imp = pd.DataFrame(sorted(zip(importance, self.features)), columns=['Value','Feature'])
        top_3 = feature_imp.tail(3)['Feature'].tolist()
        return f"Decision based on high importance of: {', '.join(top_3)}"
