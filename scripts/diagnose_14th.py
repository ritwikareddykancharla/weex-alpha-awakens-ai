import pandas as pd
import numpy as np
import os

def calculate_indicators(df):
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    df['ema_100'] = df['close'].ewm(span=100).mean()
    df['ema_200'] = df['close'].ewm(span=200).mean()
    
    # Squeeze Diagnostic
    ema_cols = ['ema_20', 'ema_50', 'ema_100', 'ema_200']
    ema_min = df[ema_cols].min(axis=1)
    ema_max = df[ema_cols].max(axis=1)
    df['spread_pct'] = (ema_max - ema_min) / df['close']
    
    # Funding Rate (Simulated for history)
    df['funding_rate'] = (df['close'].pct_change(288).rolling(50).mean() * 0.1).fillna(0.0001)
    return df

def run_diagnostic():
    data_path = "data/yfinance_btc_5m.csv"
    if not os.path.exists(data_path):
        print("❌ Data not found")
        return
        
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = calculate_indicators(df)
    
    # Filter for the 14th
    df_14 = df[(df['datetime'] >= '2026-01-14') & (df['datetime'] < '2026-01-15')]
    
    if df_14.empty:
        print("❌ No data for the 14th")
        return
        
    print(f"--- Diagnostic for Jan 14th ---")
    print(df_14[['datetime', 'close', 'spread_pct', 'funding_rate']].describe())
    
    # Find points with lowest spread
    tightest = df_14.sort_values('spread_pct').head(10)
    print("\n--- Top 10 Tightest Clusters ---")
    print(tightest[['datetime', 'spread_pct', 'funding_rate', 'close']])
    
    # Check threshold 0.0015
    squeeze_count = (df_14['spread_pct'] < 0.0015).sum()
    print(f"\nSqueeze points (< 0.15%): {squeeze_count}")

if __name__ == "__main__":
    run_diagnostic()
