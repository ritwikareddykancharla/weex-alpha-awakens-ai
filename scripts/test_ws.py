import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.websocket_client import WeexWSClient

def on_price_update(data):
    """Callback when new data arrives"""
    # Data is a list, usually one item for kline
    candle = data[0] if isinstance(data, list) else data
    print(f"🔥 LIVE: {candle.get('close')} (Vol: {candle.get('size')})")

def main():
    print("Initializing WebSocket...")
    ws = WeexWSClient()
    ws.start()
    
    # Wait a sec for connection
    time.sleep(2)
    
    # Subscribe to 1-minute candles for BTC
    # Format: kline.{priceType}.{contractId}.{interval}
    channel = "kline.LAST_PRICE.cmt_btcusdt.MINUTE_1"
    ws.subscribe(channel, on_price_update)
    
    print("Listening for 30 seconds... (Press Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
