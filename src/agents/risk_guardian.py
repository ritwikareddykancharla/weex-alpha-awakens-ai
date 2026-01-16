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
            return {"approved": False, "reason": "High Volatility Regime"}
            
        # 2. Leverage Check (Not fully implemented without position sizing)
        # Placeholder for complex risk logic
        
        return {"approved": True, "reason": "Risk Checks Passed"}
        
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
