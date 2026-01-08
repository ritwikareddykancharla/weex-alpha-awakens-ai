#!/usr/bin/env python3
"""
Script to train AI model for trading strategy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os

from src.api.weex_client import WeexAPIClient
from src.strategy.signals.ai_model import AIModel
from src.utils.logger import setup_logger
from config.settings import config

logger = setup_logger(__name__)

def fetch_training_data(symbol: str, days: int = 90) -> pd.DataFrame:
    """Fetch historical data for training"""
    api_client = WeexAPIClient()
    
    # Calculate start time
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    logger.info(f"Fetching {days} days of data for {symbol}...")
    
    all_klines = []
    batch_size = 1000  # API limit
    
    # Fetch in batches
    current_start = start_time
    while current_start < end_time:
        try:
            # Convert to timestamp (milliseconds)
            start_ts = int(current_start.timestamp() * 1000)
            end_ts = int(min(current_start + timedelta(days=7), end_time).timestamp() * 1000)
            
            # Fetch klines
            klines = api_client._request(
                "GET",
                f"/capi/v2/market/klines",
                params={
                    "symbol": symbol,
                    "interval": "1h",
                    "startTime": start_ts,
                    "endTime": end_ts,
                    "limit": batch_size
                }
            )
            
            if klines:
                all_klines.extend(klines)
            
            # Move to next batch
            current_start += timedelta(days=7)
            
        except Exception as e:
            logger.error(f"Error fetching data batch: {e}")
            break
    
    # Convert to DataFrame
    df = pd.DataFrame(all_klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume'
    ])
    
    # Convert types
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    df = df.drop_duplicates().sort_values('timestamp')
    
    logger.info(f"Fetched {len(df)} candles for {symbol}")
    return df

def main():
    """Main training function"""
    logger.info("Starting AI model training...")
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Initialize AI model
    ai_model = AIModel()
    
    # For demonstration, use BTC as primary symbol
    # In production, train on all symbols or create separate models
    symbol = "cmt_btcusdt"
    
    try:
        # Fetch training data
        data = fetch_training_data(symbol, days=180)
        
        if len(data) < 100:
            logger.error("Insufficient data for training")
            return
        
        # Generate features
        logger.info("Generating features...")
        features = ai_model.generate_features(data)
        
        # Generate labels
        logger.info("Generating labels...")
        labels = ai_model.generate_labels(data, forward_period=3)
        
        # Align features and labels
        common_idx = features.index.intersection(labels.index)
        features = features.loc[common_idx]
        labels = labels.loc[common_idx]
        
        logger.info(f"Training on {len(features)} samples")
        
        # Train model
        model_name = "gradient_boosting"
        training_result = ai_model.train_model(features, labels, model_name)
        
        # Save model and scaler
        model_path = config.MODEL_PATH
        scaler_path = config.SCALER_PATH
        
        joblib.dump(training_result['model'], model_path)
        joblib.dump(training_result['scaler'], scaler_path)
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Scaler saved to {scaler_path}")
        
        # Print feature importance
        if hasattr(training_result['model'], 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': training_result['features'],
                'importance': training_result['model'].feature_importances_
            }).sort_values('importance', ascending=False)
            
            logger.info("\nFeature Importance:")
            logger.info(importance_df.to_string())
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()
