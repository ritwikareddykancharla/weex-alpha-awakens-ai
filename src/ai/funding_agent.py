from src.utils.logger import setup_logger
import pandas as pd

logger = setup_logger(__name__)

class FundingAgent:
    """
    Core Strategy: Funding Rate Arbitrage.
    - If Funding << 0: Shorts pay Longs -> GO LONG
    - If Funding >> 0: Longs pay Shorts -> GO SHORT
    """
    def __init__(self, threshold=0.0001): # 0.01%
        self.threshold = threshold

    def analyze(self, market_data: dict, regime: int) -> dict:
        """
        Decides on action based on funding rate and regime.
        market_data: {'symbol': 'BTCUSDT', 'fundingRate': 0.0001, 'markPrice': 50000, ...}
        regime: 0 (Calm), 1 (Trend), 2 (Volatile)
        """
        funding_rate = float(market_data.get('fundingRate', 0))
        symbol = market_data.get('symbol')
        
        # Default decision
        decision = {
            "action": "NEUTRAL",
            "confidence": 0.0,
            "reason": "Funding rate within threshold"
        }

        # Filter: Don't trade funding arb in extremely volatile regimes if risk is too high
        # (Unless we are fading liquidations, which is a different agent)
        if regime == 2: 
            # High Volatility - reduce size or sit out unless opportunity is massive
            # For simplicity MVP, we skip arb in crash mode to be safe
            decision['reason'] = "Regime 2 (High Volatility) - Skipping Arb"
            return decision

        # Logic
        if funding_rate > self.threshold:
            # Positive Funding: Longs pay Shorts. We want to be SHORT to collect.
            decision = {
                "action": "SHORT",
                "confidence": min(abs(funding_rate) * 1000, 1.0), # Scaling confidence
                "reason": f"Positive Funding {funding_rate:.5f} -> Collect Shorts"
            }
        elif funding_rate < -self.threshold:
            # Negative Funding: Shorts pay Longs. We want to be LONG to collect.
            decision = {
                "action": "LONG",
                "confidence": min(abs(funding_rate) * 1000, 1.0),
                "reason": f"Negative Funding {funding_rate:.5f} -> Collect Longs"
            }
            
        return decision
