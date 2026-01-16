
import os
import time
import pandas as pd
import sys

# Ensure src is in pythonpath
sys.path.append(os.getcwd())
try:
    from src.api.weex_client import WeexAPIClient
except ImportError:
    # Fallback
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from src.api.weex_client import WeexAPIClient

SYMBOLS = ["cmt_btcusdt", "cmt_ethusdt"]
TIMEFRAMES = ["1m", "5m", "15m", "30m", "60m"]
DATA_DIR = "data"

def fetch_snapshot():
    client = WeexAPIClient()
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print(f"🚀 Fetching Latest 100 Candles for {SYMBOLS}")
    print(f"📅 Timeframes: {TIMEFRAMES}\n")
    
    for symbol in SYMBOLS:
        print(f"🟣 {symbol.upper()}")
        for tf in TIMEFRAMES:
            try:
                # Weex API specific granularity mapping if needed
                # Usually standard: 1m, 5m, 15m, 30m, 60m (or 1h)
                granularity = tf
                if tf == "60m": granularity = "1h"
                
                params = {
                    "symbol": symbol,
                    "granularity": granularity,
                    "limit": 100
                }
                
                # Fetch
                klines = client._request("GET", "/capi/v2/market/historyCandles", params=params)
                
                if klines:
                    # Parse: [time, open, high, low, close, vol, ...]
                    data = []
                    for k in klines:
                        data.append([
                            int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])
                        ])
                    
                    # Create DataFrame
                    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    # Weex returns Newest -> Oldest usually? Or Oldest -> Newest?
                    # Let's sort by timestamp ascending (Oldest -> Newest) for CSV
                    df.sort_values('timestamp', inplace=True)
                    
                    # Save
                    filename = f"{symbol.replace('/', '_')}_{tf}.csv"
                    path = os.path.join(DATA_DIR, filename)
                    df.to_csv(path, index=False)
                    
                    print(f"   ✅ {tf:<4}: Saved {len(df)} candles to {filename}")
                else:
                    print(f"   ⚠️ {tf:<4}: No data returned")
                    
                time.sleep(0.1) # Be nice
                
            except Exception as e:
                print(f"   ❌ {tf:<4}: Failed - {e}")
        print("")

if __name__ == "__main__":
    fetch_snapshot()
