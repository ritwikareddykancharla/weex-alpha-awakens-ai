from .base_agent import BaseAgent
from src.ai.regime_classifier import RegimeClassifier
# from src.ai.alpha_engine import AlphaEngine # Deprecated
from agents.dqn import WEEXDQNTradingBot, TradingFeatureEngineer
import pandas as pd
from typing import Dict, Any

class MarketAnalyst(BaseAgent):
    """
    The 'Brain' & 'Eyes' of the system.
    Combines Regime Classification (GMM) and Deep Q-Network Prediction.
    """
    def __init__(self, symbol="cmt_btcusdt", model_path_dqn="models/dqn_cmt_btcusdt.pth", model_path_gmm="models/regime_gmm.pkl"):
        super().__init__("MarketAnalyst")
        
        # 1. Eyes (Context)
        self.eyes = RegimeClassifier(model_path=model_path_gmm)
        
        # 2. Brain (Action)
        self.dqn = WEEXDQNTradingBot(symbol=symbol)
        try:
            self.dqn.load_model(model_path_dqn)
            self.logger.info(f"🧠 DQN Brain Loaded: {model_path_dqn}")
            self.is_brain_loaded = True
        except Exception as e:
            self.logger.error(f"⚠️ DQN Brain NOT Loaded: {e}")
            self.is_brain_loaded = False
        
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        1. Detect Regime (Risk Context)
        2. Predict Direction (DQN)
        """
        df = market_data.get('klines_df')
        if df is None or df.empty:
            return {"signal": "NEUTRAL", "confidence": 0, "reason": "No Data"}

        # 1. Detect Regime
        regime = self.eyes.predict(df)
        regime_label = ["CALM", "TRENDING", "VOLATILE"][regime]
        
        # 2. Predict Signal (DQN)
        if not self.is_brain_loaded:
             return {"signal": "NEUTRAL", "confidence": 0, "reason": "Brain Not Loaded"}

        # Prepare features for DQN
        features = TradingFeatureEngineer.compute_features(df)
        latest_features = features[-1]
        
        # Get portfolio context (Mock for now, will connect to real balance later)
        # TODO: Pass real balance/position from Coordinator
        balance = market_data.get('balance', 1000.0)
        position_size = market_data.get('position_size', 0.0)
        current_price = df['close'].iloc[-1]
        
        prediction = self.dqn.predict(
            current_features=latest_features,
            balance=balance,
            position=position_size,
            current_price=current_price
        )
        
        # Convert DQN action (BUY/SELL/HOLD) to standard Agent Signal
        action = prediction['action']
        if action == "HOLD":
            signal = "NEUTRAL"
        elif action == "BUY":
            signal = "LONG"
        elif action == "SELL":
            signal = "SHORT"
            
        return {
            "signal": signal,
            "confidence": prediction['confidence'],
            "regime": regime_label,
            "raw_regime": regime,
            "reason": f"DQN Action: {action} ({prediction['confidence']:.2%})"
        }
