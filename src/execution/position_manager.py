from typing import Dict, List, Optional
from src.api.weex_client import WeexAPIClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PositionManager:
    """
    Manages active positions, handles exits, and reallocates capital.
    Directly interfaces with WeexAPIClient to execute closures.
    """
    def __init__(self, weex_client: WeexAPIClient, stop_loss_pct: float = 0.02):
        self.weex = weex_client
        self.stop_loss_pct = stop_loss_pct
        self.positions: Dict[str, Dict] = {} # Cache of open positions {symbol: position_data}

    def sync_positions(self):
        """Fetches latest positions from Exchange."""
        try:
            raw_positions = self.weex.get_positions()
            # Reset cache
            self.positions = {}
            for pos in raw_positions:
                # Weex returns a list, filter for non-zero size
                if float(pos.get('size', 0)) > 0:
                    symbol = pos['symbol'].lower().replace("cmt_", "") # Normalize to "dogeusdt"
                    self.positions[symbol] = pos
            
            logger.info(f"Synced Positions: {len(self.positions)} active trades.")
        except Exception as e:
            logger.error(f"Failed to sync positions: {e}")

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Returns position data for a symbol if it exists."""
        return self.positions.get(symbol.lower())

    def check_exit_conditions(self, symbol: str, new_signal: str, current_price: float):
        """
        Evaluates if an existing position should be closed based on:
        1. Signal Flip (Alpha Engine says NEUTRAL/OPPOSITE).
        2. Stop Loss (PnL < Threshold).
        """
        position = self.get_position(symbol)
        if not position:
            return

        side = "LONG" if position['side'] == 1 else "SHORT" # Weex side 1=Long, 2=Short
        size = float(position['size'])
        entry_price = float(position['openPrice'])
        
        # Calculate PnL %
        if side == "LONG":
            pnl_pct = (current_price - entry_price) / entry_price
        else:
            pnl_pct = (entry_price - current_price) / entry_price

        # 1. Stop Loss Check
        if pnl_pct < -self.stop_loss_pct:
            logger.warning(f"STOP LOSS TRIGGERED for {symbol}: PnL {pnl_pct:.2%}")
            self.close_position(symbol, size, side, reason="STOP_LOSS")
            return

        # 2. Signal Flip Check
        # If we are LONG and Signal is NEUTRAL or SHORT -> CLOSE
        if side == "LONG" and new_signal in ["NEUTRAL", "SHORT"]:
            logger.info(f"Signal Flip for {symbol}: LONG -> {new_signal}. Closing.")
            self.close_position(symbol, size, side, reason="SIGNAL_FLIP")

        # If we are SHORT and Signal is NEUTRAL or LONG -> CLOSE
        elif side == "SHORT" and new_signal in ["NEUTRAL", "LONG"]:
            logger.info(f"Signal Flip for {symbol}: SHORT -> {new_signal}. Closing.")
            self.close_position(symbol, size, side, reason="SIGNAL_FLIP")

    def close_position(self, symbol: str, size: float, side: str, reason: str):
        """Executes a market close order."""
        try:
            # To close a LONG, we SELL. To close a SHORT, we BUY.
            action = "SELL" if side == "LONG" else "BUY"
            
            self.weex.place_order(
                symbol=symbol,
                side=action,
                order_type="MARKET",
                quantity=size
            )
            logger.info(f"CLOSED {symbol} ({side}) | Reason: {reason}")
            
            # Remove from cache immediately
            if symbol.lower() in self.positions:
                del self.positions[symbol.lower()]
                
        except Exception as e:
            logger.error(f"Failed to close {symbol}: {e}")
