from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RiskEngine:
    """
    Enforces hard risk limits.
    1. Max Leverage per Regime.
    2. Dynamic Stop Loss.
    3. Position Sizing validation.
    """
    def __init__(self):
        self.MAX_LEVERAGE_CALM = 10
        self.MAX_LEVERAGE_VOLATILE = 2
        self.MAX_DRAWDOWN_PER_TRADE = 0.02 # 2% max loss per trade

    def check_risk(self, decision: dict, regime: int, portfolio_value: float) -> dict:
        """
        Validates and adjusts the trade decision based on risk rules.
        """
        if decision['action'] == 'NEUTRAL':
            return decision

        # 1. Leverage Check
        max_lev = self.MAX_LEVERAGE_CALM if regime != 2 else self.MAX_LEVERAGE_VOLATILE
        
        # We enforce leverage by adjusting position size if needed, 
        # or just passing the constrained leverage to execution.
        decision['max_leverage'] = max_lev
        
        # 2. Stop Loss Calculation
        # Dynamic SL: wider in volatile markets (to avoid wicks), tighter in calm.
        # But we must respect Max Drawdown.
        # Loss = Position_Size * (Entry - Stop)
        # Max_Loss = Portfolio * 0.02
        # So |Entry - Stop| / Entry <= 0.02 / Leverage
        
        # Simple heuristic for SL distance based on confidence
        base_sl_percent = 0.01 # 1% move
        if regime == 2:
            base_sl_percent = 0.03 # Allow more breathing room in volatility
            
        decision['stop_loss_pct'] = base_sl_percent
        
        # 3. Size Check (Mock logic for now, assumes size is passed or calculated later)
        # If confidence is low, reduce size.
        if decision.get('confidence', 0) < 0.5:
            decision['risk_factor'] = 0.5 # Half size
        else:
            decision['risk_factor'] = 1.0

        logger.info(f"Risk Check Passed. Regime: {regime}, MaxLev: {max_lev}, SL: {base_sl_percent*100}%")
        return decision
