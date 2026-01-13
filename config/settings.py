import os
from dataclasses import dataclass, field
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TradingConfig:
    """Trading configuration"""
    # Competition pairs
    TRADING_PAIRS: List[str] = field(default_factory=lambda: [
        "cmt_btcusdt", "cmt_ethusdt", "cmt_bnbusdt",
        "cmt_solusdt", "cmt_xrpusdt", "cmt_adausdt",
        "cmt_dogeusdt", "cmt_ltcusdt"
    ])
    
    # Risk management
    MAX_LEVERAGE: int = 20
    MAX_POSITION_SIZE: float = 0.1  # 10% per trade
    DAILY_LOSS_LIMIT: float = 0.05  # 5% daily loss limit
    STOP_LOSS_PCT: float = 0.02     # 2% stop loss
    TAKE_PROFIT_RATIO: float = 2.0  # 1:2 risk-reward
    
    # AI Model
    MODEL_PATH: str = "models/trend_classifier.pkl"
    SCALER_PATH: str = "models/scaler.pkl"
    CONFIDENCE_THRESHOLD: float = 0.65
    
    # Trading parameters
    LOOKBACK_PERIOD: int = 100
    TREND_CONFIRMATION_BARS: int = 3
    MIN_TRADE_AMOUNT: float = 10.0  # USDT minimum
    
    # API
    API_KEY: str = os.getenv("WEEX_API_KEY", "")
    SECRET_KEY: str = os.getenv("WEEX_SECRET_KEY", "")
    PASSPHRASE: str = os.getenv("WEEX_PASSPHRASE", "")
    BASE_URL: str = "https://api-contract.weex.com"
    
    # Execution
    USE_TESTNET: bool = False
    ORDER_TIMEOUT: int = 30  # seconds
    MAX_RETRIES: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    AI_LOG_PATH: str = "logs/ai_trading.log"
    SAVE_TRADES_CSV: bool = True

config = TradingConfig()
