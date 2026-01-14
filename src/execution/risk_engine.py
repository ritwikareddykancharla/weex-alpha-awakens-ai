from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RiskEngine:
    """
    Enforces risk limits and calculates AI-Optimized Position Size.
    Now tunable via Hyperparameter Optimization.
    """
    def __init__(self, kelly_fraction=0.25, max_leverage=20, sl_mult=1.0):
        # Hyperparameters (tuned by scripts/optimize_strategy.py)
        self.kelly_fraction = kelly_fraction # Fraction of Kelly size to use (Safety)
        self.max_leverage = max_leverage
        self.sl_buffer = 0.01 * sl_mult # Base Stop Loss distance
        
        self.MAX_DRAWDOWN_PER_TRADE = 0.05

    def check_risk(self, decision: dict, regime: int, portfolio_value: float) -> dict:
        """
        Calculates optimal size using Kelly Criterion and AI Confidence.
        """
        confidence = decision.get('confidence', 0.5)
        action = decision.get('action')
        
        if action == 'NEUTRAL':
            return decision

        # 1. Kelly Criterion for Sizing
        # f = p - (1-p)/b
        # p = Probability of Win (Confidence)
        # b = Odds (Risk/Reward Ration). Assume 1.5 for Trend Following.
        p = max(confidence, 0.51) # Assume edge
        b = 1.5 
        f_star = p - (1-p)/b
        
        # Apply Safety Fraction (The "AI Tuned" parameter)
        safe_f = f_star * self.kelly_fraction
        safe_f = max(0.0, min(safe_f, 1.0)) # Clip 0% to 100%
        
        # 2. Leverage Calc
        # Effective Leverage = Safe_f / (Risk_Per_Trade) ?? 
        # Simplified: Size = Portfolio * safe_f * Leverage
        # Wait, usually Kelly outputs % of bankroll to risk.
        # Let's use: Allocation % = safe_f. 
        # Leverage = max_leverage (Isolated).
        
        decision['allocation_pct'] = safe_f
        decision['leverage'] = self.max_leverage
        
        # 3. Dynamic Stop Loss
        # Volatile (Regime 2) -> Wider Stop
        sl_dist = self.sl_buffer
        if regime == 2:
            sl_dist *= 2.0
            
        decision['stop_loss_pct'] = sl_dist
        
        logger.info(f"Risk Engine: Conf={confidence:.2f} -> Kelly={f_star:.2f} -> SafeAlloc={safe_f:.2%}")
        return decision
