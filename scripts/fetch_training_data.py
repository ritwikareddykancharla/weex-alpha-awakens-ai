import os
import time
import pandas as pd
from datetime import datetime
import sys

# Ensure src is in pythonpath
sys.path.append(os.getcwd())
from src.api.weex_client import WeexAPIClient

# Target Pairs for Hackathon
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT",
    "XRP/USDT", "ADA/USDT", "DOT/USDT", "LINK/USDT"
]

def fetch_single_pair(symbol, days=30):
    print(f"📥 Fetching {symbol} for last {days} days...")
    
    # Calculate timestamps
    end_time_ms = int(time.time() * 1000)
    start_time_limit = end_time_ms - (days * 24 * 60 * 60 * 1000)
    
    all_klines = []
    current_end = end_time_ms
    
    client = WeexAPIClient()
    
    # Batch loop
    while current_end > start_time_limit:
        batch_size = 100
        
        try:
            params = {
                "symbol": symbol,
                "granularity": "1m", # 1 minute candles
                "limit": batch_size,
                "endTime": current_end
            }
            klines = client._request("GET", "/capi/v2/market/historyCandles", params=params)
            
            if not klines or len(klines) == 0:
                print(f"   Stopping: No more data returned for {symbol}")
                break
                
            # Response: [time, open, high, low, close, vol, vol_quote]
            processed_klines = []
            for k in klines:
                processed_klines.append([
                    int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])
                ])

            if not processed_klines:
                break

            all_klines.extend(processed_klines)
            
            # Update timestamp for next batch
            timestamps = [k[0] for k in processed_klines]
            min_ts = min(timestamps)
            current_end = min_ts - 60000 # Go back 1 minute
            
            # Print status every 1000 candles
            if len(all_klines) % 1000 == 0:
                print(f"   Fetched {len(all_klines)} candles. Reached: {datetime.fromtimestamp(min_ts/1000)}")
            
            time.sleep(0.1) # Rate limit protection
            
        except Exception as e:
            print(f"Error fetching batch: {e}")
            break
            
    # Save to CSV
    if all_klines:
        # Create 'data' folder at root
        os.makedirs("data", exist_ok=True)
        
        df = pd.DataFrame(all_klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # Sort ascending
        df = df.sort_values('timestamp').reset_index(drop=True)
        df = df.drop_duplicates(subset=['timestamp'])
        
        filename = f"data/{symbol.replace('/', '_')}_1m.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(df)} rows to {filename}")
    else:
        print(f"⚠️ No data fetched for {symbol}")

if __name__ == "__main__":
    for sym in SYMBOLS:
        fetch_single_pair(sym)
