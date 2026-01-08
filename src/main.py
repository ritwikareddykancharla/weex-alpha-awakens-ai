#!/usr/bin/env python3
"""
Main entry point for WEEX AI Trading Strategy
"""

import asyncio
import signal
import sys
from datetime import datetime

from src.api.weex_client import WeexAPIClient
from src.strategy.ai_trend_follower import AITrendFollower
from src.utils.logger import ai_logger, setup_logger
from config.settings import config

logger = setup_logger(__name__)

class TradingBot:
    """Main trading bot controller"""
    
    def __init__(self):
        self.api_client = WeexAPIClient()
        self.strategy = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize trading bot"""
        logger.info("Initializing WEEX AI Trading Bot...")
        
        # Test API connection
        if not self.api_client.test_connection():
            logger.error("API connection failed. Check credentials and network.")
            return False
        
        logger.info("API connection successful")
        
        # Check account balance
        try:
            balance = self.api_client.get_account_balance()
            usdt_balance = next(
                (float(item['available']) for item in balance 
                 if item['coinName'] == 'USDT'), 0
            )
            logger.info(f"Account balance: {usdt_balance:.2f} USDT")
            
            if usdt_balance < config.MIN_TRADE_AMOUNT:
                logger.warning(
                    f"Balance below minimum trade amount ({config.MIN_TRADE_AMOUNT} USDT)"
                )
                
        except Exception as e:
            logger.error(f"Failed to check balance: {e}")
        
        # Initialize strategy
        self.strategy = AITrendFollower(self.api_client)
        
        # Log initialization
        ai_logger.log_risk({
            "event": "BOT_INITIALIZED",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "trading_pairs": config.TRADING_PAIRS,
                "max_leverage": config.MAX_LEVERAGE,
                "daily_loss_limit": config.DAILY_LOSS_LIMIT
            }
        })
        
        return True
    
    async def run(self):
        """Main execution loop"""
        if not await self.initialize():
            logger.error("Initialization failed. Exiting.")
            return
        
        self.is_running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("Starting trading strategy...")
        
        try:
            # Run strategy
            await self.strategy.execute_strategy()
            
        except asyncio.CancelledError:
            logger.info("Strategy execution cancelled")
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
        finally:
            await self.shutdown()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}. Shutting down...")
        self.is_running = False
        
        # Cancel all tasks
        for task in asyncio.all_tasks():
            task.cancel()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down trading bot...")
        
        # Close all positions (optional - be careful with this)
        # await self.close_all_positions()
        
        # Generate final log summary
        summary = ai_logger.get_log_summary()
        logger.info(f"Final log summary: {summary}")
        
        # Log shutdown
        ai_logger.log_risk({
            "event": "BOT_SHUTDOWN",
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        })
        
        logger.info("Shutdown complete")

async def main():
    """Main entry point"""
    bot = TradingBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
