import time
from src.api.weex_client import WeexAPIClient
from src.data.coingecko_loader import CoinGeckoLoader
from src.ai.regime_classifier import RegimeClassifier
from src.ai.funding_agent import FundingAgent
from src.execution.risk_engine import RiskEngine
from src.utils.logger import setup_logger
import pandas as pd
import json

logger = setup_logger("MainOrchestrator")

def run_loop():
    logger.info("Starting WEEX AI Hackathon Bot (Perp-Optimized)...")
    
    # Initialize Components
    weex = WeexAPIClient()
    cg = CoinGeckoLoader()
    classifier = RegimeClassifier()
    funding_agent = FundingAgent()
    risk_engine = RiskEngine()
    
    # Config
    symbol = "cmt_dogeusdt" # Example pair from docs
    
    # Main Loop
    while True:
        try:
            logger.info("--- New Cycle ---")
            
            # 1. Market Discovery (CoinGecko Track)
            # Find opportunities or just get context
            opportunities = cg.scan_market_opportunities()
            if not opportunities.empty:
                logger.info(f"Top CG Opp: {opportunities.iloc[0]['symbol']} (Vol: {opportunities.iloc[0]['volatility_score']:.2f}%)")
            
            # 2. Fetch Data (WEEX)
            ticker = weex.get_ticker(symbol)
            # Simulate generic 'market_data' dict for agents
            current_price = float(ticker.get('close', 0)) # hypothetical field
            funding_data = weex.get_funding_rate_history(symbol, page_size=1)
            latest_funding = float(funding_data[0]['fundingRate']) if funding_data else 0.0
            
            # Get specific klines for Regime Classifier
            klines = weex.get_klines(symbol, interval="15m", limit=50)
            # Parse klines to DF: [time, open, high, low, close, volume, ...]
            # Adjust index based on actual API response format (assuming standard list)
            df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'a', 'b'])
            df['close'] = df['close'].astype(float)
            df['fundingRate'] = latest_funding # Approximate for recent history if history not detailed enough
            
            # 3. AI Regime Classification
            if len(df) > 20:
                classifier.fit(df) # Online learning / Refit
                regime = classifier.predict(df)
            else:
                regime = 0 # Default Calm
                
            # 4. Strategy Signal
            market_context = {
                'symbol': symbol,
                'fundingRate': latest_funding,
                'markPrice': current_price
            }
            decision = funding_agent.analyze(market_context, regime)
            
            # 5. Risk Check
            # Assume portfolio value 1000 for mock
            decision = risk_engine.check_risk(decision, regime, portfolio_value=1000)
            
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
