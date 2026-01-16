from src.utils.logger import setup_logger
import pandas as pd

logger = setup_logger(__name__)

class AlphaEngine:
    """
    Alpha Engine (DQN Signal Generator).
    Generates 'LONG', 'SHORT', 'NEUTRAL' signals based on Neural Network prediction.
    """
    def __init__(self, model_path="models/trend_classifier.pkl"):
        self.logger = setup_logger("AlphaEngine")
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        import os
        import joblib
        
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                
                # Try load scaler too
                scaler_path = self.model_path.replace("trend_classifier.pkl", "scaler.pkl")
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                    
                self.logger.info(f"✅ Loaded ML Model from {self.model_path}")
            except Exception as e:
                self.logger.error(f"Failed to load ML model: {e}")
        else:
            self.logger.warning(f"No model found at {self.model_path}. Run 'python scripts/train_local.py' first.")

    def analyze(self, market_data: dict, regime: int, historical_data: pd.DataFrame = None) -> dict:
        """
        Predicts LONG/SHORT/NEUTRAL using Gradient Boosting.
        """
        # 1. Feature Engineering
        if historical_data is None or len(historical_data) < 20:
             return {"action": "NEUTRAL", "confidence": 0.0, "reason": "Insufficient Data"}
            
        from src.strategy.signals.ai_model import AIModel
        ai = AIModel()
        
        try:
            # Generate features exactly like training
            features = ai.generate_features(historical_data)
            
            if features.empty:
                return {"action": "NEUTRAL", "confidence": 0, "reason": "No Features"}
            
            # Get latest row
            latest_features = features.iloc[[-1]]
            
            # 2. Prediction
            if self.model and self.scaler:
                signal, confidence = ai.predict(latest_features, self.model, self.scaler)
                
                return {
                    "action": signal,
                    "confidence": confidence,
                    "reason": f"ML Model Signal (Conf: {confidence:.2f})"
                }
            else:
                return {"action": "NEUTRAL", "confidence": 0, "reason": "Model Not Loaded"}
                
        except Exception as e:
            self.logger.error(f"Analysis Failed: {e}")
            return {"action": "NEUTRAL", "confidence": 0, "reason": "Error"}
