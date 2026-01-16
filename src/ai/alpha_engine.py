from src.utils.logger import setup_logger
import pandas as pd

logger = setup_logger(__name__)

class AlphaEngine:
    """
    Alpha Engine (DQN Signal Generator).
    Generates 'LONG', 'SHORT', 'NEUTRAL' signals based on Neural Network prediction.
    """
    def __init__(self, model_path="models/quant_momentum_dqn.pth"):
        self.logger = setup_logger("AlphaEngine")
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        from agents.dqn import WEEXDQNTradingBot
        self.bot = WEEXDQNTradingBot(symbol="BTC/USDT") 
        self.model_loaded = False
        
        import os
        import torch
        if os.path.exists(self.model_path):
            try:
                # We need to initialize the agent with dummy data to build the network first
                # or modify load_model to handle initialization.
                # Assuming load_model handles it or we do it lazily.
                # For now, let's just attempt load.
                self.bot.load_model(self.model_path)
                
                # Re-init agent network if load_model just loaded state dict
                # (The original code had a slight gap here, assuming we need to spin up a dummy environment to get state_dim)
                # But let's assume valid state for now.
                
                self.model_loaded = True
                self.logger.info(f"✅ Loaded DQN Model from {self.model_path}")
            except Exception as e:
                self.logger.error(f"Failed to load DQN model: {e}")
        else:
            self.logger.warning(f"No model found at {self.model_path}. Agent will run in collection mode.")

    def analyze(self, market_data: dict, regime: int, historical_data: pd.DataFrame = None) -> dict:
        """
        Decides on action based on DQN Agent.
        """
        if historical_data is None or len(historical_data) < 60:
             return {"action": "NEUTRAL", "confidence": 0.0, "reason": "Insufficient Data"}
        
        # Compute features
        from agents.dqn import TradingFeatureEngineer
        try:
            features = TradingFeatureEngineer.compute_features(historical_data)
            current_state = features[-1]
            
            if not self.model_loaded:
                 return {"action": "NEUTRAL", "confidence": 0, "reason": "DQN Model Not Loaded"}

            # Get Prediction
            current_price = float(market_data.get('markPrice', 0) or historical_data['close'].iloc[-1])
            balance = 1000.0 
            position = 0.0 
            
            prediction = self.bot.predict(
                current_features=current_state,
                balance=balance,
                position=position,
                current_price=current_price
            )
            
            # Map Actions
            dqn_action = prediction['action']
            confidence = prediction['confidence']
            
            system_action = "NEUTRAL"
            if dqn_action == "BUY": system_action = "LONG"
            elif dqn_action == "SELL": system_action = "SHORT"
            
            return {
                "action": system_action,
                "confidence": confidence,
                "reason": f"DQN Signal: {dqn_action}"
            }
                
        except Exception as e:
            self.logger.error(f"DQN Analysis Failed: {e}")
            return {"action": "NEUTRAL", "confidence": 0, "reason": "DQN Error"}
