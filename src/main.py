import time
from src.api.weex_client import WeexAPIClient
from src.data.coingecko_loader import CoinGeckoLoader
from src.ai.regime_classifier import RegimeClassifier
from src.ai.alpha_engine import AlphaEngine
from src.execution.position_manager import PositionManager

# ... imports ...

def run_loop():
    logger.info("Starting WEEX AI Hackathon Bot (Perp-Optimized)...")
    
    # Initialize Components
    weex = WeexAPIClient()
    classifier = RegimeClassifier()
    alpha_engine = AlphaEngine(model_path="models/trend_classifier.pkl")
    risk_engine = RiskEngine()
    position_manager = PositionManager(weex) # New Component
    
    # Load Active Portfolio (Dynamic)
    # ... (loading logic stays same) ...
    
    # Main Loop
    while True:
        try:
            logger.info("--- New Cycle ---")
            
            # 0. Sync Portfolio State (Critical for Reallocation)
            position_manager.sync_positions()
            
            # ... (Regime Classification stays same) ...
                
            # 4. Strategy Analysis (DQN Agent)
            # Pass historical data to the Agent for feature engineering
            decision = alpha_engine.analyze(
                market_data={
                    "symbol": symbol,
                    "fundingRate": latest_funding,
                    "markPrice": current_price
                },
                regime=regime,
                historical_data=df
            )
            
            # 4.5 Position Management (Exit Logic)
            # Before entering new trades, check if we need to close existing ones
            position_manager.check_exit_conditions(
                symbol=symbol,
                new_signal=decision['action'],
                current_price=current_price
            )
            
            # 5. Risk Check & entry logic...
            # If we already have a position that wasn't closed, we might skip entry?
            # Ideally, PositionManager closes it if signal flips. 
            # If signal adheres, we might add size or hold.
            # For simplicity: If position exists, we skip 'Entry' logic to avoid double-betting
            if position_manager.get_position(symbol):
                logger.info(f"Holding existing position on {symbol}. Skipping new entry.")
                continue

            # ... rest of entry logic ...
            
            # 6. Execution & Logging
            if decision['action'] != "NEUTRAL":
                log_entry = {
                    "timestamp": time.time(),
                    "regime": int(regime),
                    "action": decision['action'],
                    "symbol": symbol,
                    "funding_rate": latest_funding,
                    "confidence": decision.get('confidence', 0),
                    "max_leverage": decision.get('max_leverage', 1),
                    "features": {
                        "cg_volatility_top": float(opportunities.iloc[0]['volatility_score']) if not opportunities.empty else 0
                    }
                }
                
                # Write to "AI Log" for Hackathon (critical requirement)
                with open("ai_trading_log.json", "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
                    
                logger.info(f"EXECUTED: {decision['action']} | {decision['reason']}")
            else:
                logger.info("No Trade (Neutral)")
                
            # Sleep
            time.sleep(60) # 1 min loop
            
        except Exception as e:
            logger.error(f"Loop Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_loop()
