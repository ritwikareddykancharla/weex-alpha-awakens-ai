import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.api.weex_client import WeexAPIClient
from config.settings import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class RiskMetrics:
    """Risk metrics for a trading session"""
    daily_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    profitable_trades: int = 0

class RiskManager:
    """Advanced risk management system"""
    
    def __init__(self, api_client: WeexAPIClient):
        self.api_client = api_client
        self.metrics = RiskMetrics()
        self.daily_trades = []
        self.session_start = datetime.now()
        
        # Load volatility data
        self.volatility_cache = {}
    
    def calculate_position_size(self, symbol: str, 
                               confidence: float) -> float:
        """
        Calculate position size based on risk parameters
        
        Uses Kelly Criterion with modifications for crypto volatility
        """
        try:
            # Get account balance
            balance_data = self.api_client.get_account_balance()
            usdt_balance = next(
                (float(item['available']) for item in balance_data 
                 if item['coinName'] == 'USDT'), 0
            )
            
            if usdt_balance <= 0:
                return 0
            
            # Get volatility for the symbol
            volatility = self._get_symbol_volatility(symbol)
            
            # Modified Kelly formula
            # Position size = (confidence * win_probability - loss_probability) / volatility
            win_prob = min(confidence, 0.8)  # Cap at 80%
            loss_prob = 1 - win_prob
            
            # Kelly fraction
            kelly_fraction = (win_prob * 2.0 - loss_prob) / volatility
            
            # Apply conservative caps
            kelly_fraction = min(kelly_fraction, 0.1)  # Max 10% per trade
            kelly_fraction = max(kelly_fraction, 0.01)  # Min 1% per trade
            
            # Adjust for daily loss limit
            daily_loss_used = abs(min(self.metrics.daily_pnl, 0))
            daily_loss_remaining = config.DAILY_LOSS_LIMIT - daily_loss_used
            
            if daily_loss_remaining <= 0:
                return 0
            
            # Final position size
            position_size = usdt_balance * kelly_fraction
            position_size = min(position_size, 
                               daily_loss_remaining * 2)  # Cap at 2x daily loss remaining
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    def _get_symbol_volatility(self, symbol: str) -> float:
        """Calculate recent volatility for a symbol"""
        if symbol in self.volatility_cache:
            cache_time, volatility = self.volatility_cache[symbol]
            if datetime.now() - cache_time < timedelta(hours=1):
                return volatility
        
        try:
            # Get recent klines for volatility calculation
            klines = self.api_client.get_klines(
                symbol, interval="1h", limit=24
            )
            
            if len(klines) < 20:
                return 0.02  # Default 2% volatility
            
            closes = [float(k[4]) for k in klines]
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns) * np.sqrt(365)  # Annualized
            
            # Cache the result
            self.volatility_cache[symbol] = (datetime.now(), volatility)
            
            return max(volatility, 0.01)  # Minimum 1%
            
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol}: {e}")
            return 0.02
    
    def calculate_sl_tp(self, entry_price: float, side: str,
                       confidence: float) -> Tuple[float, float]:
        """
        Calculate stop loss and take profit levels
        """
        # Dynamic stop loss based on volatility and confidence
        base_sl_pct = config.STOP_LOSS_PCT
        
        # Adjust SL based on confidence
        confidence_multiplier = 1.0 + (1.0 - confidence)  # Higher confidence = tighter SL
        sl_pct = base_sl_pct * confidence_multiplier
        
        # Calculate levels
        if side == 'BUY':
            stop_loss = entry_price * (1 - sl_pct)
            take_profit = entry_price * (1 + sl_pct * config.TAKE_PROFIT_RATIO)
        else:  # SELL
            stop_loss = entry_price * (1 + sl_pct)
            take_profit = entry_price * (1 - sl_pct * config.TAKE_PROFIT_RATIO)
        
        return stop_loss, take_profit
    
    def check_daily_limit(self) -> bool:
        """Check if daily loss limit is reached"""
        # Calculate today's P&L
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        
        # In production, you'd fetch actual trades from API
        # For now, use cached metrics
        daily_loss = abs(min(self.metrics.daily_pnl, 0))
        
        if daily_loss >= config.DAILY_LOSS_LIMIT:
            logger.warning(f"Daily loss limit reached: {daily_loss:.2%}")
            return False
        
        return True
    
    def update_metrics(self, trade_result: Dict):
        """Update risk metrics after a trade"""
        self.metrics.total_trades += 1
        
        if trade_result.get('pnl', 0) > 0:
            self.metrics.profitable_trades += 1
        
        self.metrics.daily_pnl += trade_result.get('pnl', 0)
        self.metrics.win_rate = (
            self.metrics.profitable_trades / 
            max(self.metrics.total_trades, 1)
        )
        
        # Store trade for analysis
        self.daily_trades.append({
            **trade_result,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_risk_report(self) -> Dict:
        """Generate risk report"""
        return {
            'daily_pnl': self.metrics.daily_pnl,
            'daily_pnl_percent': self.metrics.daily_pnl / 1000,  # Based on 1000 USDT
            'win_rate': self.metrics.win_rate,
            'total_trades': self.metrics.total_trades,
            'daily_loss_used': abs(min(self.metrics.daily_pnl, 0)),
            'daily_loss_remaining': max(
                config.DAILY_LOSS_LIMIT - abs(min(self.metrics.daily_pnl, 0)), 
                0
            ),
            'current_positions': len(self.daily_trades),
            'session_duration': str(datetime.now() - self.session_start)
        }
