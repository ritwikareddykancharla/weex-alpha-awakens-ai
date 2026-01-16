import pandas as pd
import os
import argparse
from agents.dqn import WEEXDQNTradingBot

# Create 'models' directory if it doesn't exist
os.makedirs("models", exist_ok=True)

def train_brain(symbol, csv_path, episodes=50, fine_tune_episodes=10):
    print(f"\n🧠 STARTING TRAINING FOR {symbol}...")
    print(f"📄 Data Source: {csv_path}")
    
    # 1. Load Data
    try:
        df = pd.read_csv(csv_path)
        # Ensure timestamp is datetime for potential sorting/filtering
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        print(f"📊 Loaded {len(df)} candles")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return

    # 2. Split Data (Recency Bias Strategy)
    # Strategy: 
    # - Base Train: First 90% of data (General Knowledge)
    # - Fine Tune: Last 10% of data (Current Meta)
    
    split_idx = int(len(df) * 0.90)
    base_df = df.iloc[:split_idx]
    recent_df = df.iloc[split_idx:]
    
    print(f"📅 Base Data: {len(base_df)} candles | Recent Data: {len(recent_df)} candles")

    # 3. Base Training
    bot = WEEXDQNTradingBot(symbol=symbol)
    
    print("\n🏋️ [Phase 1] Base Training (General Pattern Recognition)...")
    base_metrics = bot.train(base_df, episodes=episodes)
    
    base_model_path = f"models/dqn_{symbol}_base.pth"
    bot.save_model(base_model_path)
    print(f"✅ Base Model Saved: {base_model_path}")

    # 4. Fine-Tuning (Recency Bias)
    print("\n🎨 [Phase 2] Fine-Tuning (Adapting to Recent Market)...")
    
    # Lower learning rate for fine-tuning to avoid catastrophic forgetting
    # Access internal agent config (Hack)
    if bot.agent:
        bot.agent.config["learning_rate"] = 1e-5 
        bot.agent.optimizer.param_groups[0]['lr'] = 1e-5
        print("   -> Lowered Learning Rate to 1e-5")

    tune_metrics = bot.train(recent_df, episodes=fine_tune_episodes)
    
    # 5. Save Final Brain
    final_model_path = f"models/dqn_{symbol}.pth"
    bot.save_model(final_model_path)
    print(f"\n🎉 SUCCESS! Final Brain Saved: {final_model_path}")
    print("   -> Copy this file to your bot's 'models' folder.")

if __name__ == "__main__":
    # Example Usage: run from command line
    # python scripts/train_dqn.py --symbol cmt_btcusdt --data data/btc_15m.csv
    
    parser = argparse.ArgumentParser(description='Train Weex DQN Brain')
    parser.add_argument('--symbol', type=str, required=True, help='Trading Pair (e.g., cmt_btcusdt)')
    parser.add_argument('--data', type=str, required=True, help='Path to CSV data file')
    parser.add_argument('--episodes', type=int, default=50, help='Base training episodes')
    parser.add_argument('--tune', type=int, default=10, help='Fine-tuning episodes')
    
    args = parser.parse_args()
    
    train_brain(args.symbol, args.data, args.episodes, args.tune)
