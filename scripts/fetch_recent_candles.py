
import sys
import os
import pandas as pd
import numpy as np
# from tabulate import tabulate
# Actually let's use standard printing to avoid dependency issues if tabulate isn't installed.

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.weex_client import WeexAPIClient

def analyze_candles():
    client = WeexAPIClient()
    symbols = ["cmt_btcusdt", "cmt_ethusdt"]
    intervals = ["1m", "5m", "15m", "30m", "60m", "4h"] # Weex usually uses 60m or 1h, let's try 60m based on common API patterns, or 1h. 
    # Checking get_klines implementation: granularity=interval.
    # Common Weex values: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w. Let's try "1h" and "4h".
    intervals = ["1m", "5m", "15m", "30m", "1h", "4h"]

    print(f"\n{'='*60}")
    print(f"🔎 WEEX MARKET VOLATILITY ANALYSIS (Last 100 Candles)")
    print(f"{'='*60}\n")

    for symbol in symbols:
        print(f"🟣 {symbol.upper()}")
        print(f"{'-'*75}")
        print(f"{'Interval':<10} | {'Current Price':<15} | {'Avg Range (Vol)':<18} | {'Change (100)':<15}")
        print(f"{'-'*75}")

        for interval in intervals:
            try:
                # Fetch Data
                klines = client.get_klines(symbol, interval=interval, limit=100)
                if not klines:
                    print(f"{interval:<10} | {'NO DATA':<15} | {'-':<18} | {'-':<15}")
                    continue
                
                # Parse Data
                # Klines format usually: [time, open, high, low, close, vol, ...]
                # WeexClient returns list of lists.
                df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'])
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['open'] = df['open'].astype(float)

                # Analysis
                current_price = df['close'].iloc[-1]
                
                # Volatility: Average (High - Low) / Close
                df['range_pct'] = (df['high'] - df['low']) / df['close'] * 100
                avg_volatility = df['range_pct'].mean()
                
                # Change over last 100 candles
                start_price = df['open'].iloc[0]
                total_change_pct = ((current_price - start_price) / start_price) * 100
                
                # Format Output
                vol_str = f"{avg_volatility:.3f}%"
                change_str = f"{total_change_pct:+.2f}%"
                
                print(f"{interval:<10} | ${current_price:<14.2f} | {vol_str:<18} | {change_str:<15}")

            except Exception as e:
                print(f"{interval:<10} | Error: {str(e)}")
        
        print("\n")

if __name__ == "__main__":
    analyze_candles()
