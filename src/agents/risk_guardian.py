from .base_agent import BaseAgent
from typing import Dict, Any

class RiskGuardian(BaseAgent):
    """
    The 'Shield' of the system.
    Has VETO power over all trades.
    """
    def __init__(self, max_leverage=20, max_drawdown=0.05):
        super().__init__("RiskGuardian")
        self.max_leverage = max_leverage
        self.max_daily_drawdown = max_drawdown
        self.initial_balance = None # To track DD
        
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a trade is safe to execute.
        Requires 'proposed_action' and 'regime' in market_data.
        """
        proposed_action = market_data.get('proposed_action', 'NEUTRAL')
        regime = market_data.get('regime', 'CALM')
        
        # 1. Regime Veto
        # If market is Crashing/Volatile (Regime 2), we block all entries
        if regime == "VOLATILE" and proposed_action != "NEUTRAL":
            self.logger.warning("🚫 VETO: Market is too volatile for entry.")
            return {"approved": False, "reason": "High Volatility Regime", "size": 0.0}
            
        # 2. Risk Calculation (ATR Based)
        # "Turtle Trading" Sizing: Equal Risk per Trade
        # Size = (Balance * Risk_Perc) / (ATR * Stop_Mult)
        
        balance = float(market_data.get('balance', 0))
        price = float(market_data.get('price', 0))
        atr = self._calculate_atr(market_data.get('candles', []))
        
        # Default risk 10% per trade (HACKATHON MODE: AGGRESSIVE GROWTH)
        # Goal: Maximize ROI in 2 weeks.
        risk_per_trade = 0.10 
        stop_mult = 1.5 # Tighten stop slightly to allow larger size
        
        if atr > 0 and price > 0:
            dollar_risk = balance * risk_per_trade
            unit_stop_dist = atr * stop_mult
            
            # How many units can we buy such that if it hits stop, we lose $risk?
            # Loss = Size * Stop_Dist
            # Size = Loss / Stop_Dist
            safe_size = dollar_risk / unit_stop_dist
            
            # Cap at Max Leverage (e.g. 10x) just in case ATR is tiny
            max_leverage_size = (balance * self.max_leverage) / price
            final_size = min(safe_size, max_leverage_size)
            
            # Convert to lot precision (simplified)
            final_size = round(final_size, 4)
            
            self.logger.info(f"🛡️ Sizing: ATR={atr:.2f} | Risk=${dollar_risk:.2f} | Size={final_size} (MaxLev={max_leverage_size:.2f})")
        else:
            # Fallback if no ATR (shouldn't happen)
            final_size = (balance * 0.05) / price # Fixed 5% fallback
            self.logger.warning("⚠️ No ATR found, using fixed 5% size.")

        return {
            "approved": True, 
            "reason": "Risk Checks Passed",
            "suggested_size": final_size,
            "stop_loss_dist": atr * stop_mult if atr > 0 else price * 0.02
        }

    def _calculate_atr(self, candles: list, period=14) -> float:
        """
        Calculate ATR manually from OHLCV list.
        Candle format: [time, open, high, low, close, volume]
        """
        if not candles or len(candles) < period + 1:
            return 0.0
            
        try:
            # Extract Highs, Lows, Closes
            # Assume candles are sorted ascending (oldest first)
            # Standard TA-Lib TR logic: Max(H-L, |H-Cp|, |L-Cp|)
            
            tr_list = []
            for i in range(1, len(candles)):
                curr_h = float(candles[i][2])
                curr_l = float(candles[i][3])
                prev_c = float(candles[i-1][4])
                
                tr = max(curr_h - curr_l, abs(curr_h - prev_c), abs(curr_l - prev_c))
                tr_list.append(tr)
            
            # Simple Moving Average of TR for ATR (Wilder uses EMA, SMA is fine proxy)
            # Use last 'period' TRs
            recent_tr = tr_list[-period:]
            atr = sum(recent_tr) / len(recent_tr)
            return atr
            
        except Exception as e:
            self.logger.error(f"Failed to calc ATR: {e}")
            return 0.0

    def check_portfolio_risk(self, account_data: Dict) -> bool:
        """
        Check global portfolio health (Drawdown, Margin Ratio).
        Returns False if we should STOP trading.
        """
        current_equity = float(account_data.get('equity', 0))
        if self.initial_balance is None:
            self.initial_balance = current_equity
            
        if self.initial_balance <= 0: return True 
        
        drawdown = (self.initial_balance - current_equity) / self.initial_balance
        
        if drawdown > self.max_daily_drawdown:
            self.logger.critical(f"🛑 KILL SWITCH: Drawdown {drawdown:.2%} > Limit {self.max_daily_drawdown:.2%}")
            return False
            
        return True
