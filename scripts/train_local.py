import pandas as pd
import glob
import os
import joblib
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.strategy.signals.ai_model import AIModel
from src.utils.logger import setup_logger
from config.settings import config

logger = setup_logger("LocalTrainer")

def load_local_data(data_dir="data"):
    """Load and merge all CSV files from data directory"""
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not all_files:
        logger.error(f"No CSV files found in {data_dir}")
        return pd.DataFrame()
    
    logger.info(f"Found {len(all_files)} files: {[os.path.basename(f) for f in all_files]}")
    
    df_list = []
    for filename in all_files:
        df = pd.read_csv(filename)
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        elif 'time' in df.columns:
            df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
            
        df_list.append(df)
        
    full_df = pd.concat(df_list, ignore_index=True)
    full_df = full_df.sort_values('timestamp').drop_duplicates('timestamp').reset_index(drop=True)
    return full_df

def main():
    logger.info("Starting Local Training...")
    
    # 1. Load Data
    df = load_local_data()
    if df.empty:
        return
        
    logger.info(f"Loaded {len(df)} total candles.")
    
    # 2. Build Features
    ai_model = AIModel()
    logger.info("Generating Features...")
    try:
        # Standardize columns if needed
        # Expected: open, high, low, close, volume (or vol)
        if 'vol' in df.columns and 'volume' not in df.columns:
            df['volume'] = df['vol']
            
        features = ai_model.generate_features(df)
        labels = ai_model.generate_labels(df, forward_period=3)
        
        # Align
        common_idx = features.index.intersection(labels.index)
        features = features.loc[common_idx]
        labels = labels.loc[common_idx]
        
        logger.info(f"Training set size: {len(features)}")
        
        # 3. Train
        train_result = ai_model.train_model(features, labels, "gradient_boosting")
        
        # 4. Save
        os.makedirs("models", exist_ok=True)
        joblib.dump(train_result['model'], "models/trend_classifier.pkl")
        joblib.dump(train_result['scaler'], "models/scaler.pkl")
        
        logger.info("✅ SUCCESS: Model and Scaler saved to 'models/' folder.")
        
    except Exception as e:
        logger.error(f"Training Failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
