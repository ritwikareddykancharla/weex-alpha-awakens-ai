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
        self.bot = None
        self._load_model()
        self.model_loaded = False # This line is kept as it was in the original code, but its value will be set by _load_model

    def _load_model(self):
        # Lazy import to avoid circular dependencies if any
        from agents.dqn import WEEXDQNTradingBot
        self.bot = WEEXDQNTradingBot(symbol="BTC/USDT") # Symbol updated per request
        
        # Try load model
        import os
        if os.path.exists(self.model_path):
            try:
                self.bot.load_model(self.model_path)
                self.bot.agent.epsilon = 0.01 # Low exploration for inference
                self.model_loaded = True
                logger.info(f"Loaded DQN Model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load DQN model: {e}")
        else:
            logger.warning(f"No model found at {self.model_path}. Agent will run in collection/fallback mode.")

    def analyze(self, market_data: dict, regime: int, historical_data: pd.DataFrame = None) -> dict:
        """
        Decides on action based on DQN Agent.
        market_data: {'symbol': 'BTCUSDT', 'fundingRate': ..., 'markPrice': ...}
        historical_data: DataFrame of klines for feature engineering
        """
        # 1. Feature Engineering & State Prep
        if historical_data is None or len(historical_data) < 60:
             return {
                "action": "NEUTRAL",
                "confidence": 0.0,
                "reason": "Insufficient historical data for DQN"
            }
            
        current_price = float(market_data.get('markPrice', 0))
        balance = 1000.0 # Mock balance if not passed, or fetch from args if we update signature
        position = 0.0 # Mock position
        
        # Compute features using the bot's engineer
        from agents.dqn import TradingFeatureEngineer
        try:
            features = TradingFeatureEngineer.compute_features(historical_data)
            current_state = features[-1]
            
            # 2. Get Prediction
            if self.model_loaded:
                prediction = self.bot.predict(
                    current_features=current_state,
                    balance=balance,
                    position=position,
                    current_price=current_price
                )
                
                # Map DQN actions (BUY/SELL/HOLD) to System Actions (LONG/SHORT/NEUTRAL)
                # DQN: 0=HOLD, 1=BUY (Long), 2=SELL (Short)
                dqn_action = prediction['action']
                confidence = prediction['confidence']
                
                system_action = "NEUTRAL"
                if dqn_action == "BUY": system_action = "LONG"
                elif dqn_action == "SELL": system_action = "SHORT"
                
                return {
                    "action": system_action,
                    "confidence": confidence,
                    "reason": f"DQN Model {dqn_action} (Conf: {confidence:.2f})"
                }
            else:
                # Fallback: Collection Mode (Use dummy logic or simple rules while training)
                return {
                    "action": "NEUTRAL",
                    "confidence": 0.0,
                    "reason": "Model not loaded - Data Collection Mode"
                }
                
        except Exception as e:
            logger.error(f"DQN Analysis Failed: {e}")
            return {"action": "NEUTRAL", "confidence": 0, "reason": "DQN Error"}
