
import pandas as pd
import numpy as np
import torch
import sys
import os

# Add Project Root to Path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Agents from 'agents' folder (since dqn.py is in agents/, not src/agents/)
# Adjusting based on file structure check: 
# dqn.py is in 'agents/dqn.py' (root/agents) or 'src/agents/dqn.py'?
# Checking file path from earlier: c:\Users\hp\Desktop\weex-alpha-awakens-ai\agents\dqn.py
# So it is NOT in src.agents. It is in agents.

from agents.dqn import DQNAgent, TradingFeatureEngineer, HACKATHON_CONFIG

def calculate_heuristic_action(df, idx):
    """
    Simple Strategy:
    Long if Price > EMA 12 > EMA 26
    Short if Price < EMA 12 < EMA 26
    """
    if idx < 30: return 0 # Hold (Not enough data)
    
    price = df['close'].iloc[idx]
    ema12 = df['ema_12'].iloc[idx]
    ema26 = df['ema_26'].iloc[idx]
    
    # 0 = Hold, 1 = Long, 2 = Short (Assuming Action Dim=3)
    if price > ema12 > ema26:
        return 1 # BUY
    elif price < ema12 < ema26:
        return 2 # SELL
    else:
        return 0 # HOLD

def train_local():
    # 1. Load Data (Using YFinance Data as requested for validation)
    data_path = "data/yfinance_btc_15m.csv"
    if not os.path.exists(data_path):
        print(f"❌ Data not found at {data_path}. Run fetch scripts first.")
        return
        
    df = pd.read_csv(data_path)
    print(f"📉 Loaded {len(df)} candles from {data_path}")
    
    # 2. Preprocess
    print("🧠 Engineering Features...")
    engineer = TradingFeatureEngineer()
    features = engineer.compute_features(df)
    
    # Add EMAs for Heuristic Calculation
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    
    # 3. Initialize Agent
    state_dim = features.shape[1]
    action_dim = 3 # Hold, Buy, Sell
    
    agent = DQNAgent(state_dim, action_dim, HACKATHON_CONFIG, device="cpu")
    print(f"🤖 Agent Initialized. State Dim: {state_dim}")
    
    # 4. Training Loop
    epochs = 3 
    print(f"🚀 Starting Training ({epochs} Epochs)...")
    
    # Trace specific moments in time to see evolution
    DEBUG_STEPS = [4000, 4001, 4002, 4003, 4004] 
    
    feature_names = [
        "Returns", "LogRet", 
        "ROC5", "ROC15", "ROC30", 
        "Vol15", "Vol30", "Vol60", 
        "EMA12_Diff", "EMA26_Diff", 
        "RSI", "Vol_MA", "Spread", "ATR", 
        "Dist_Res", "Dist_Sup", "Funding"
    ]

    for epoch in range(epochs):
        total_reward = 0
        positive_rewards = 0
        negative_rewards = 0
        
        # WE MUST TRACK STATE: Are we currently Long, Short, or Out?
        # 0=Flat, 1=Long, 2=Short
        current_position = 0 
        entry_price = 0.0
        
        # Walk through time (Step-by-Step)
        # We start at index 100 to allow for lookback windows
        for t in range(100, len(df) - 1):
            state = features[t]
            next_state = features[t+1]
            
            # --- WARM START MAGIC ---
            # Calculate what the "Old School Strategy" would do
            heuristic = calculate_heuristic_action(df, t)
            
            # Ask the Agent (Passing the Cheat Sheet)
            action = agent.select_action(state, training=True, heuristic_action=heuristic)
            
            # Market Data
            current_price = df['close'].iloc[t]
            next_price = df['close'].iloc[t+1]
            price_change_pct = (next_price - current_price) / current_price
            
            # --- REWARD CALCULATION (Realism Upgrade) ---
            step_reward = 0.0
            
            # 1. Calculate PnL if we are holding a position
            if current_position == 1: # Long
                step_reward += price_change_pct * 100
            elif current_position == 2: # Short
                step_reward -= price_change_pct * 100
            
            # 2. Apply Transaction Costs (The "Activation Energy")
            # If we change state (Buy/Sell), we pay the fee
            if action != current_position:
                # Cost is typically 0.1% (dummy value: 0.1)
                # Since our reward is scaled by 100, 0.1% = 0.1 reward points
                fee_penalty = 0.1 
                step_reward -= fee_penalty
                
            # 3. Small penalty for sitting in cash (optional, encourages active digging)
            # if action == 0: step_reward -= 0.001
            
            # Update Position for next step
            current_position = action
                
            # Track stats
            if step_reward > 0: positive_rewards += 1
            if step_reward < 0: negative_rewards += 1
                
            # Store in Memory
            done = (t == len(df) - 2)
            agent.store_transition(state, action, step_reward, next_state, done)
            
            # Learn
            loss = agent.update()
            total_reward += step_reward
            
            # --- DEEP DIVE LOGGING ---
            if t in DEBUG_STEPS:
                # ... (Logging logic remains the same)
                action_str = ["HOLD", "BUY", "SELL"][action]
                print(f"\n🔍 [EPOCH {epoch+1} | STEP {t}]")
                print(f"   Price: {current_price:.2f} -> {next_price:.2f} (Change: {price_change_pct*100:.4f}%)")
                print(f"   🤖 Action: {action_str} | Fee Paid: {'YES' if action !=0 else 'NO'}")
                print(f"   🍪 Reward: {step_reward:.4f}")
                print("-" * 40)

            if t % 1000 == 0:
                print(f"   Epoch {epoch+1} | Step {t} | Epsilon: {agent.epsilon:.4f} | R: {total_reward:.2f}")

        # Update Target Network
        agent.target_network.load_state_dict(agent.q_network.state_dict())
        print(f"✅ Epoch {epoch+1} Complete. Total Reward: {total_reward:.2f} (Wins: {positive_rewards} | Losses: {negative_rewards})")

    # Save
    torch.save(agent.q_network.state_dict(), "models/dqn_btc_local.pth")
    print("💾 Model Saved: models/dqn_btc_local.pth")

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    train_local()
