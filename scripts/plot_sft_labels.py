"""
Visualize the Expert Labels (BUY/SELL/HOLD) generated for SFT Training.
Shows where the EMA Cloud Strategy would tell you to trade.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def generate_labels_and_plot():
    # 1. Load Data
    data_path = "data/yfinance_btc_15m.csv"
    if not os.path.exists(data_path):
        print(f"❌ Data not found at {data_path}.")
        return
        
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    print(f"📉 Loaded {len(df)} candles")
    
    # 2. Calculate EMAs
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    
    # 3. Generate Labels - RSI ONLY
    df['label'] = 0  # Default: HOLD
    
    # Calculate RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # BUY: RSI crosses ABOVE 30 (Exiting Oversold)
    # SELL: RSI crosses BELOW 70 (Exiting Overbought)
    
    for i in range(1, len(df)):
        rsi_now = df['rsi'].iloc[i]
        rsi_prev = df['rsi'].iloc[i-1]
        
        if rsi_prev <= 30 and rsi_now > 30:
            df.iloc[i, df.columns.get_loc('label')] = 1  # BUY
            
        elif rsi_prev >= 70 and rsi_now < 70:
            df.iloc[i, df.columns.get_loc('label')] = 2  # SELL
    
    print(f"   Labels: HOLD={len(df[df['label']==0])}, BUY={len(df[df['label']==1])}, SELL={len(df[df['label']==2])}")
    
    # 5. Plot (Last 7 days for clarity)
    df_plot = df.tail(672).copy()
    
    # Create 2 subplots (Price + RSI)
    fig, (ax, ax_rsi) = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    ax_rsi.set_facecolor('#f8f9fa')
    
    # --- SUBPLOT 1: PRICE ---
    # Plot Price Range Shading (High-Low)
    ax.fill_between(df_plot['datetime'], df_plot['low'], df_plot['high'], 
                    color='#cccccc', alpha=0.3, label='H-L Range', zorder=1)
    
    # Plot Price line
    ax.plot(df_plot['datetime'], df_plot['close'], color='#333333', linewidth=1, label='BTC Price', alpha=0.8, zorder=3)
    
    # Plot EMAs
    ax.plot(df_plot['datetime'], df_plot['ema_12'], color='#2196F3', linewidth=1.5, label='EMA 12', alpha=0.7)
    ax.plot(df_plot['datetime'], df_plot['ema_26'], color='#FF9800', linewidth=1.5, label='EMA 26', alpha=0.7)
    
    # EMA Cloud
    ax.fill_between(df_plot['datetime'], df_plot['ema_12'], df_plot['ema_26'],
                    where=(df_plot['ema_12'] >= df_plot['ema_26']),
                    color='green', alpha=0.15, label='Bullish Zone')
    ax.fill_between(df_plot['datetime'], df_plot['ema_12'], df_plot['ema_26'],
                    where=(df_plot['ema_12'] < df_plot['ema_26']),
                    color='red', alpha=0.15, label='Bearish Zone')
    
    # Plot BUY signals (Green Triangles)
    buy_df = df_plot[df_plot['label'] == 1]
    ax.scatter(buy_df['datetime'], buy_df['close'], 
               marker='^', color='green', s=100, label=f'BUY Signals ({len(buy_df)})', zorder=5, edgecolors='white')
    
    # Plot SELL signals (Red Triangles)
    sell_df = df_plot[df_plot['label'] == 2]
    ax.scatter(sell_df['datetime'], sell_df['close'], 
               marker='v', color='red', s=100, label=f'SELL Signals ({len(sell_df)})', zorder=5, edgecolors='white')
    
    ax.set_title('EMA Crossover Analysis + RSI (Last 7 Days)', fontsize=16, fontweight='bold')
    ax.set_ylabel('BTC Price (USDT)', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # --- SUBPLOT 2: RSI ---
    ax_rsi.plot(df_plot['datetime'], df_plot['rsi'], color='#9C27B0', linewidth=1.5, label='RSI (14)')
    ax_rsi.axhline(70, color='red', linestyle='--', alpha=0.5)
    ax_rsi.axhline(30, color='green', linestyle='--', alpha=0.5)
    ax_rsi.axhline(50, color='gray', linestyle=':', alpha=0.3)
    
    # Shade Overbought/Oversold
    ax_rsi.fill_between(df_plot['datetime'], df_plot['rsi'], 70, where=(df_plot['rsi'] >= 70), color='red', alpha=0.2)
    ax_rsi.fill_between(df_plot['datetime'], df_plot['rsi'], 30, where=(df_plot['rsi'] <= 30), color='green', alpha=0.2)
    
    ax_rsi.set_ylabel('RSI', fontsize=12)
    ax_rsi.set_ylim(0, 100)
    ax_rsi.grid(True, alpha=0.3)
    
    # Date formatting
    ax_rsi.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax_rsi.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save
    output_path = "sft_labels_visualization.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✨ Plot saved to {output_path}")
    plt.close()


if __name__ == "__main__":
    generate_labels_and_plot()
