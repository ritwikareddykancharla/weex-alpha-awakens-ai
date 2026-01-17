import yfinance as yf
import pandas as pd
import os

def fetch_5m_data():
    print("🚀 Fetching 1 month of 5m BTC data from yfinance...")
    ticker = "BTC-USD"
    # yfinance max for 5m is 60 days, 1mo is perfect
    df = yf.download(ticker, period="1mo", interval="5m")
    
    if df.empty:
        print("❌ Failed to fetch data.")
        return
        
    # Robustly flatten and rename
    df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    
    mapping = {
        'Datetime': 'datetime',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }
    # Case-insensitive mapping
    new_cols = []
    for col in df.columns:
        found = False
        for k, v in mapping.items():
            if col.lower() == k.lower():
                new_cols.append(v)
                found = True
                break
        if not found:
            new_cols.append(col)
    df.columns = new_cols
    
    # Save to data folder
    os.makedirs("data", exist_ok=True)
    save_path = "data/yfinance_btc_5m.csv"
    df.to_csv(save_path, index=False)
    print(f"✅ Saved {len(df)} 5m candles to {save_path}")
    print(f"   Columns: {list(df.columns)}")

if __name__ == "__main__":
    fetch_5m_data()
