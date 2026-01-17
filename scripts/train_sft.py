"""
Supervised Fine-Tuning (SFT) Training Script
Trains the DQN model to IMITATE the EMA Cloud Strategy.
This is Behavioral Cloning / Imitation Learning.
"""
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import sys
import os

# Add Project Root to Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.dqn import DuelingQNetwork, TradingFeatureEngineer, HACKATHON_CONFIG


def calculate_stoch_rsi(series, period=14, smooth_k=3):
    # RSI
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Stoch RSI
    rsi_min = rsi.rolling(window=period).min()
    rsi_max = rsi.rolling(window=period).max()
    stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min)
    
    k = stoch_rsi.rolling(window=smooth_k).mean() * 100
    return k

def detect_ema_squeeze(df, threshold_pct=0.0015):
    """Detect points where EMAs (20, 50, 100) are tightly compressed"""
    ema_cols = ['ema_20', 'ema_50', 'ema_100']
    ema_min = df[ema_cols].min(axis=1)
    ema_max = df[ema_cols].max(axis=1)
    spread_pct = (ema_max - ema_min) / df['close']
    return spread_pct < threshold_pct

def generate_expert_labels(df: pd.DataFrame) -> np.ndarray:
    """
    Generate labels based on a hybrid strategy:
    1. SQUEEZE EXPLOSION: High-volatility breakouts from EMA clusters.
    2. RIBBON BOUNCE: Trend-following pullbacks confirmed by StochRSI.
    """
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    df['ema_100'] = df['close'].ewm(span=100).mean()
    df['ema_200'] = df['close'].ewm(span=200).mean()
    df['stoch_k'] = calculate_stoch_rsi(df['close'])
    df['is_squeeze'] = detect_ema_squeeze(df)
    
    labels = np.zeros(len(df), dtype=np.int64)
    
    for i in range(10, len(df)):
        price_now = df['close'].iloc[i]
        price_prev = df['close'].iloc[i-1]
        stoch_k = df['stoch_k'].iloc[i]
        ema20 = df['ema_20'].iloc[i]
        ema50 = df['ema_50'].iloc[i]
        ema100 = df['ema_100'].iloc[i]
        
        # --- 1. SQUEEZE BREAKOUT (Explosion) ---
        was_squeezed = any(df['is_squeeze'].iloc[i-10:i])
        if was_squeezed and not df['is_squeeze'].iloc[i]:
            ema_max = max(ema20, ema50, ema100)
            ema_min = min(ema20, ema50, ema100)
            
            # Breakout Up
            if price_now > ema_max and price_prev <= ema_max:
                labels[i] = 1 # BUY
                continue
            # Breakout Down
            elif price_now < ema_min and price_prev >= ema_min:
                labels[i] = 2 # SELL
                continue
        
        # --- 2. RIBBON BOUNCE (Trend Flow) ---
        # UP TREND
        if ema50 > ema100:
            dipped = any(df['low'].iloc[i-5:i] < df['ema_20'].iloc[i-5:i])
            if dipped and price_now > ema20 and price_prev <= df['ema_20'].iloc[i-1] and stoch_k < 80:
                labels[i] = 1 # BUY
                
        # DOWN TREND
        elif ema50 < ema100:
            rallied = any(df['high'].iloc[i-5:i] > df['ema_20'].iloc[i-5:i])
            if rallied and price_now < ema20 and price_prev >= df['ema_20'].iloc[i-1] and stoch_k > 20:
                labels[i] = 2 # SELL
                
    return labels


def train_sft():
    # 1. Load Data
    data_path = "data/yfinance_btc_15m.csv"
    if not os.path.exists(data_path):
        print(f"❌ Data not found at {data_path}.")
        return
        
    df = pd.read_csv(data_path)
    print(f"📉 Loaded {len(df)} candles from {data_path}")
    
    # 2. Generate Features and Labels
    print("🧠 Engineering Features...")
    engineer = TradingFeatureEngineer()
    features = engineer.compute_features(df)
    
    print("🏷️ Generating Expert Labels (EMA Cloud Strategy)...")
    labels = generate_expert_labels(df)
    
    # Show label distribution
    unique, counts = np.unique(labels, return_counts=True)
    print(f"   Label Distribution: HOLD={counts[0]}, BUY={counts[1]}, SELL={counts[2]}")
    
    # 3. Prepare PyTorch DataLoader
    # Market Features (15 dims)
    market_X = features[100:]
    
    # Portfolio Context (4 dims: balance_norm, pos_val_norm, has_pos, dummy_pnl)
    # Using Neutral Context (1.0 balance, 0 pos, 0 flag, 0 pnl) matching WEEXDQNTradingBot
    batch_size = len(market_X)
    portfolio_X = np.zeros((batch_size, 4), dtype=np.float32)
    portfolio_X[:, 0] = 1.0  # Normalize balance
    
    # Concatenate to 19 dims
    X_numpy = np.concatenate([market_X, portfolio_X], axis=1)
    X = torch.FloatTensor(X_numpy)
    y = torch.LongTensor(labels[100:])
    
    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=128, shuffle=True)
    
    # 4. Initialize Model
    state_dim = 19  # 15 market + 4 portfolio
    action_dim = 3
    
    model = DuelingQNetwork(state_dim, action_dim, HACKATHON_CONFIG)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    
    print(f"🤖 Model Initialized. State Dim: {state_dim}")
    
    # 5. Training Loop (Supervised)
    epochs = 10
    print(f"🚀 Starting SFT Training ({epochs} Epochs)...")
    
    episodes_acc = []
    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_features, batch_labels in dataloader:
            optimizer.zero_grad()
            q_values = model(batch_features)
            loss = criterion(q_values, batch_labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(q_values, 1)
            correct += (predicted == batch_labels).sum().item()
            total += batch_labels.size(0)
        
        accuracy = 100 * correct / total
        episodes_acc.append(accuracy)
        print(f"   Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(dataloader):.4f} | Accuracy: {accuracy:.2f}%")
    
    # 6. Save Model in Format Expected by WEEXDQNTradingBot.load_model
    os.makedirs("models", exist_ok=True)
    save_path = "models/dqn_sft_ema.pth"
    
    torch.save({
        'q_network_state_dict': model.state_dict(),
        'config': HACKATHON_CONFIG,
        'training_metrics': episodes_acc,
    }, save_path)
    
    print(f"💾 Model Saved: {save_path} (Bot-Compatible Format)")
    print("✅ SFT Training Complete.")


if __name__ == "__main__":
    train_sft()
