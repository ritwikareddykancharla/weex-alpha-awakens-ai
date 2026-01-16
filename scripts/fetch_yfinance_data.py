
import yfinance as yf
import pandas as pd
import os

DATA_DIR = "data"

def fetch_yfinance_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # YFinance Tickers
    pairs = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD"
    }

    print(f"🚀 Fetching 60 Days of 15m Data from YFinance...")

    for name, ticker in pairs.items():
        try:
            # Fetch data (Max 60d for 15m)
            print(f"📥 Downloading {name} ({ticker})...")
            df = yf.download(ticker, period="60d", interval="15m", progress=False)
            
            if df.empty:
                print(f"   ⚠️ No data found for {ticker}")
                continue

            # Clean up MultiIndex columns if present (yfinance update)
            if isinstance(df.columns, pd.MultiIndex):
                # Flatten: just take the first level (Price Type)
                # Ensure we are getting 'Close', 'Open' etc, not Ticker
                df.columns = df.columns.get_level_values(0)

            # Reset index to make 'Datetime' a column
            df.reset_index(inplace=True)
            
            # Normalize columns to lowercase (Open -> open)
            df.columns = [str(c).lower() for c in df.columns]
            
            # Save
            filename = f"yfinance_{name.lower()}_15m.csv"
            path = os.path.join(DATA_DIR, filename)
            df.to_csv(path, index=False)
            
            print(f"   ✅ Saved {len(df)} candles to {filename}")
            print(f"      Range: {df['datetime'].iloc[0]} -> {df['datetime'].iloc[-1]}")
            
        except Exception as e:
            print(f"   ❌ Error fetching {name}: {e}")

if __name__ == "__main__":
    fetch_yfinance_data()
