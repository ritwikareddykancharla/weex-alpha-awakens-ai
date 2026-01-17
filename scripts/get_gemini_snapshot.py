import pandas as pd
import numpy as np

def calculate_indicators(df):
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    df['ema_100'] = df['close'].ewm(span=100).mean()
    df['ema_200'] = df['close'].ewm(span=200).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Squeeze (20, 50, 100)
    ema_cols = ['ema_20', 'ema_50', 'ema_100']
    ema_min = df[ema_cols].min(axis=1)
    ema_max = df[ema_cols].max(axis=1)
    df['spread_pct'] = (ema_max - ema_min) / df['close']
    df['is_squeeze'] = df['spread_pct'] < 0.0015
    
    return df

def get_snapshot():
    df = pd.read_csv("data/yfinance_btc_5m.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = calculate_indicators(df)
    
    # Get a specific interesting moment (e.g., the 14th Breakout we found earlier)
    # Or just the last row. Let's pick the "Squeeze Explosion" on the 14th if possible.
    
    target_date = "2026-01-14"
    mask = (df['datetime'] >= target_date) & (df['is_squeeze'])
    
    points = df[mask]
    if not points.empty:
        # Pick the last squeeze point before the explosion
        row = points.iloc[-1]
    else:
        # Fallback to last row
        row = df.iloc[-1]

    print("\n📋 copy-paste this into Gemini:\n")
    print("Analyze this market snapshot and decide: BUY, SELL, or HOLD?")
    print("--- MARKET SNAPSHOT ---")
    print(f"Timestamp: {row['datetime']}")
    print(f"Price: {row['close']:.2f}")
    print(f"EMA 20: {row['ema_20']:.2f}")
    print(f"EMA 50: {row['ema_50']:.2f} (Trend: {'Up' if row['ema_50'] > row['ema_100'] else 'Down'})")
    print(f"EMA 100: {row['ema_100']:.2f}")
    print(f"RSI (14): {row['rsi']:.1f}")
    print(f"EMA Squeeze: {'ACTIVE (Ready to Explode)' if row['is_squeeze'] else 'Inactive'}")
    print(f"Spread: {row['spread_pct']*100:.4f}%")
    print("-----------------------")

if __name__ == "__main__":
    get_snapshot()
