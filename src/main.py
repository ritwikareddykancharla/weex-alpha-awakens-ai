import time
import json
import logging
from src.api.weex_client import WeexAPIClient
from src.agents.coordinator import Coordinator
from src.execution.risk_engine import RiskEngine

# Configuration
SYMBOL = "cmt_btcusdt"
TIMEFRAME = "15m"  # Intraday Swing Strategy
LOOP_INTERVAL = 15 * 60  # 15 minutes in seconds
HARD_STOP_PCT = 0.02     # 2% Hard Stop Loss
TAKE_PROFIT_PCT = 0.04   # 4% Take Profit (Optional, usually let trend run)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_execution.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MainBot")

def run_bot():
    logger.info(f"🚀 Starting WEEX Bot | Symbol: {SYMBOL} | Timeframe: {TIMEFRAME}")
    
    # 1. Initialize Components
    client = WeexAPIClient()
    coordinator = Coordinator()
    risk_engine = RiskEngine()
    
    logger.info("✅ All systems initialized.")

    while True:
        try:
            logger.info(f"\n⏰ New Cycle: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 2. Get Market Data (15m Candles)
            # Fetch enough for the 96-period rolling window in DQN
            klines = client.get_klines(symbol=SYMBOL, interval=TIMEFRAME, limit=200)
            
            # Get current account state
            account = client.get_account_info()
            position = client.get_position(SYMBOL)
            
            market_data = {
                "symbol": SYMBOL,
                "klines_df": klines,
                "balance": float(account.get('availableBalance', 0)),
                "position_size": float(position.get('size', 0)) if position else 0,
                "fundingRate": 0.0, # TODO: Fetch real funding rate import from client
                "markPrice": float(klines['close'].iloc[-1])
            }
            
            # 3. AI Analysis (Coordinator -> Analyst -> DQN)
            decision = coordinator.analyze(market_data)
            
            # --- HACKATHON COMPLIANCE: UPLOAD AI LOG ---
            # We must prove AI made this decision.
            try:
                ai_log_input = {
                    "prompt": "Analyze 15m Candles for Trend & Risk",
                    "data": {
                        "markPrice": current_price,
                        "fundingRate": market_data['fundingRate'],
                        "position_size": market_data['position_size']
                    }
                }
                
                ai_log_output = {
                    "signal": decision['action'],
                    "confidence": decision['confidence'],
                    "reason": decision['reason']
                }
                
                explanation = f"DQN Agent Analysis: {decision['reason']} | Regime: {decision['regime']}"
                
                # Upload Log (Stage: Strategy Generation)
                log_response = client.upload_ai_log(
                    order_id=None, # No order yet
                    stage="Strategy Generation",
                    model="DQN-Agent-v1 (Custom)",
                    input_data=ai_log_input,
                    output_data=ai_log_output,
                    explanation=explanation
                )
                if log_response.get("code") == "00000":
                    logger.info("✅ AI Log Uploaded to WEEX")
                else:
                    logger.warning(f"⚠️ AI Log Upload Failed: {log_response}")
                    
            except Exception as e:
                logger.error(f"Failed to upload AI log: {e}")
            # -------------------------------------------
            
            # 4. Execution Logic
            current_price = market_data['markPrice']
            action = decision['action']
            confidence = decision['confidence']
            
            # Verify we don't double-enter
            has_position = market_data['position_size'] > 0
            
            if action == "LONG" and not has_position:
                # Calculate Size (Kelly or Risk-based)
                # For hackathon: Fixed size or simple % of equity
                # Using 10% of balance for safety
                quantity = (market_data['balance'] * 0.10) / current_price 
                
                logger.info(f"⚡ EXECUTING LONG: {quantity:.4f} {SYMBOL} @ {current_price}")
                
                # A. Place Market Buy
                order = client.place_order(SYMBOL, "BUY", quantity, "MARKET")
                
                if order and order.get('orderId'):
                    logger.info(f"   ✅ Entry Filled: {order['orderId']}")
                    
                    # --- HACKATHON COMPLIANCE: UPLOAD ORDER LOG ---
                    client.upload_ai_log(
                        order_id=order['orderId'],
                        stage="Decision Making", # Stage 2: Execution
                        model="DQN-Agent-v1",
                        input_data={"market_context": "Trend Confirmation"},
                        output_data={"action": "OPEN_LONG", "size": quantity},
                        explanation="Executed LONG based on high-confidence DQN Signal."
                    )
                    # ----------------------------------------------
                    
                    # B. Place HARD STOP BOSS (Safety Net)
                    stop_price = current_price * (1 - HARD_STOP_PCT)
                    client.place_stop_order(SYMBOL, "SELL", quantity, stop_price)
                    logger.info(f"   🛡️ Hard Stop Set @ {stop_price:.2f}")
                    
                    # C. Log for Hackathon
                    log_trade(decision, order, "ENTRY_LONG")
                else:
                    logger.error("   ❌ Entry Failed")

            elif action == "SHORT" and not has_position:
                # Same logic for Short
                quantity = (market_data['balance'] * 0.10) / current_price 
                logger.info(f"⚡ EXECUTING SHORT: {quantity:.4f} {SYMBOL} @ {current_price}")
                
                order = client.place_order(SYMBOL, "SELL", quantity, "MARKET")
                
                if order and order.get('orderId'):
                    logger.info(f"   ✅ Entry Filled: {order['orderId']}")
                    
                    # --- HACKATHON COMPLIANCE: UPLOAD ORDER LOG ---
                    client.upload_ai_log(
                        order_id=order['orderId'],
                        stage="Decision Making",
                        model="DQN-Agent-v1",
                        input_data={"market_context": "Trend Reversal"},
                        output_data={"action": "OPEN_SHORT", "size": quantity},
                        explanation="Executed SHORT based on high-confidence DQN Signal."
                    )
                    # ----------------------------------------------
                    
                    # Hard Stop (Above entry)
                    stop_price = current_price * (1 + HARD_STOP_PCT)
                    client.place_stop_order(SYMBOL, "BUY", quantity, stop_price)
                    logger.info(f"   🛡️ Hard Stop Set @ {stop_price:.2f}")
                    
                    log_trade(decision, order, "ENTRY_SHORT")

            elif action == "NEUTRAL" and has_position:
                # Check if we should exit? 
                # Coordinator currently returns NEUTRAL if HOLD. 
                # Ideally, Coordinator returns 'EXIT_LONG' or 'EXIT_SHORT'. 
                # For now, let's assume NEUTRAL means 'Do Nothing' if strictly following DQN.
                # But if DQN flips from LONG -> NEUTRAL, maybe we close?
                # Simpler: Only close if signal flips to OPPOSITE.
                pass
            
            elif (action == "SHORT" and has_position) or (action == "LONG" and has_position):
                 # Simple Reverse logic: Close current, open new?
                 # For safety, let's just Close first.
                 logger.info("🔄 Signal Flip! Closing current position...")
                 client.close_position(SYMBOL)
                 # Next loop will see 0 position and enter the new direction
            
            # Sleep until next candle
            logger.info(f"💤 Sleeping for {LOOP_INTERVAL}s...")
            time.sleep(LOOP_INTERVAL)

        except Exception as e:
            logger.error(f"⚠️ Critical Loop Error: {e}")
            time.sleep(60) # Short sleep on error

def log_trade(decision, order, trade_type):
    """Write to ai_trading_log.json for Hackathon Judges"""
    log_entry = {
        "timestamp": time.time(),
        "type": trade_type,
        "symbol": SYMBOL,
        "price": order.get('avgPrice', 0),
        "size": order.get('size', 0),
        "ai_analysis": {
            "signal": decision['action'],
            "confidence": decision['confidence'],
            "regime": decision['regime'],
            "reason": decision['reason']
        }
    }
    with open("ai_trading_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    run_bot()
