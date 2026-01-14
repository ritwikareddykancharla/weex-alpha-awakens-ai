import sys
import os
import pandas as pd
import time
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.weex_client import WeexAPIClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("DataFetcher")

def fetch_data(symbols=None, days=180, output_dir="data"):
    """
    Fetches deep historical data for multiple pairs.
    """
    if symbols is None:
        symbols = [
            "cmt_btcusdt", "cmt_ethusdt", "cmt_solusdt", "cmt_dogeusdt", 
            "cmt_xrpusdt", "cmt_adausdt", "cmt_bnbusdt", "cmt_ltcusdt"
        ]
        
    client = WeexAPIClient()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for symbol in symbols:
        logger.info(f"--- Processing {symbol} ---")
        fetch_single_pair(client, symbol, days, os.path.join(output_dir, f"{symbol}.csv"))

def fetch_single_pair(client, symbol, days, output_file):
    logger.info(f"Starting Deep Data Fetch for {symbol} (Target: {days} days)...")
    
    all_klines = []
    end_time = int(time.time() * 1000) # Now (ms)
    start_time_limit = end_time - (days * 24 * 60 * 60 * 1000)
    
    batch_size = 1000 
    
    while True:
        try:
            params = {
                "symbol": symbol,
                "interval": "15m",
                "limit": batch_size,
                "end": end_time
            }
            klines = client._request("GET", "/capi/v2/market/klines", params=params)
            
            if not klines or len(klines) == 0:
                break
                
            # Convert to DF
            batch_df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'a', 'b'])
            batch_df['time'] = batch_df['time'].astype(int)
            
            earliest_timestamp = batch_df['time'].min()
            latest_timestamp_in_batch = batch_df['time'].max()
            
            all_klines.extend(klines)
            
            prev_end_time = end_time
            end_time = earliest_timestamp - 1
            
            if end_time < start_time_limit:
                break
            if earliest_timestamp >= prev_end_time:
                break
                
            time.sleep(0.5) 
            
        except Exception as e:
            logger.error(f"Error in batch fetch: {e}")
            break
            
    if not all_klines:
        logger.error(f"No data fetched for {symbol}.")
        return

    # Process
    df = pd.DataFrame(all_klines, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'a', 'b'])
    cols = ['open', 'high', 'low', 'close', 'vol']
    for c in cols:
        df[c] = df[c].astype(float)
        
    df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
    df = df.sort_values('timestamp').drop_duplicates('time').reset_index(drop=True)
    
    # Save
    df.to_csv(output_file, index=False)
    logger.info(f"Saved {symbol}: {len(df)} candles.")

if __name__ == "__main__":
    fetch_data()
