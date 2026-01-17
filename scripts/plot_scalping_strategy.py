"""
Scalping Strategy Visualization (1-Minute Timeframe)
Strategy: Bollinger Band Mean Reversion + Stochastic RSI + EMA Filter
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def calculate_stoch_rsi(series, period=14, smooth_k=3, smooth_d=3):
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
    d = k.rolling(window=smooth_d).mean()
    return k, d

def detect_sr_levels(df, window=20, num_levels=3):
    """Detect Support and Resistance levels based on Fractal peaks/troughs"""
    # Find local highs/lows
    df['high_peak'] = df['high'].rolling(window=window, center=True).max() == df['high']
    df['low_peak'] = df['low'].rolling(window=window, center=True).min() == df['low']
    
    highs = df[df['high_peak']]['high'].tolist()
    lows = df[df['low_peak']]['low'].tolist()
    
    # Very simple clustering: sort and pick top/bottom
    if not highs or not lows:
        return [], []
        
    # Group nearby levels
    def cluster_levels(levels, tolerance_pct=0.002):
        if not levels: return []
        levels.sort()
        clusters = []
        if levels:
            curr_cluster = [levels[0]]
            for i in range(1, len(levels)):
                if levels[i] < curr_cluster[-1] * (1 + tolerance_pct):
                    curr_cluster.append(levels[i])
                else:
                    clusters.append(np.mean(curr_cluster))
                    curr_cluster = [levels[i]]
            clusters.append(np.mean(curr_cluster))
        return clusters

    res_levels = cluster_levels(highs)
    sup_levels = cluster_levels(lows)
    
    # Return most recent / significant levels
    return sorted(res_levels)[-num_levels:], sorted(sup_levels)[:num_levels]

def detect_ema_squeeze(df, threshold_pct=0.0015):
    """Detect points where EMAs (20, 50, 100) are tightly compressed"""
    ema_cols = ['ema_20', 'ema_50', 'ema_100']
    
    # Calculate min/max across EMAs
    ema_min = df[ema_cols].min(axis=1)
    ema_max = df[ema_cols].max(axis=1)
    
    # Spread as % of price
    spread_pct = (ema_max - ema_min) / df['close']
    
    # Flags points falling below threshold
    return spread_pct < threshold_pct

def generate_scalping_plot():
    # 1. Load 5m Data
    data_path = "data/yfinance_btc_5m.csv"
    if not os.path.exists(data_path):
        print(f"❌ 5m data not found at {data_path}")
        return
        
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # 2. Indicators - EMA Ribbon
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    df['ema_100'] = df['close'].ewm(span=100).mean()
    df['ema_200'] = df['close'].ewm(span=200).mean()
    
    # Stochastic RSI (Restoring)
    df['stoch_k'], df['stoch_d'] = calculate_stoch_rsi(df['close'])
    
    # Funding Rate (Simulated for history)
    df['funding_rate'] = (df['close'].pct_change(288).rolling(50).mean() * 0.1).fillna(0.0001)
    
    # 3. Scalping Signals - "RIBBON BOUNCE + RSI Confirmation"
    df['label'] = 0
    funding_threshold = 0.0005 
    
    # EMA Squeeze Detection
    df['is_squeeze'] = detect_ema_squeeze(df)
    
    for i in range(5, len(df)):
        price_now = df['close'].iloc[i]
        price_prev = df['close'].iloc[i-1]
        stoch_k = df['stoch_k'].iloc[i]
        ema20 = df['ema_20'].iloc[i]
        ema50 = df['ema_50'].iloc[i]
        ema100 = df['ema_100'].iloc[i]
        ema200 = df['ema_200'].iloc[i]
        fund = abs(df['funding_rate'].iloc[i])
        
        # --- STRATEGY A: SQUEEZE BREAKOUT (The Explosion) ---
        # Did we just come out of a squeeze in the last 10 candles?
        was_squeezed = any(df['is_squeeze'].iloc[i-10:i])
        if was_squeezed and not df['is_squeeze'].iloc[i]:
            # BREAKOUT UP: Price crosses above the cluster (20, 50, 100)
            ema_max = max(ema20, ema50, ema100)
            if price_now > ema_max and price_prev <= ema_max:
                df.iloc[i, df.columns.get_loc('label')] = 3 # SQUEEZE BUY
                continue # Prioritize breakouts

        # --- STRATEGY B: RIBBON BOUNCE (Trend Flow) ---
        # UP TREND: 50 > 100
        if ema50 > ema100 and fund < funding_threshold:
            # PULLBACK: Low of last few candles was below EMA20
            dipped = any(df['low'].iloc[i-5:i] < df['ema_20'].iloc[i-5:i])
            # BOUNCE: Close back above EMA20 + StochRSI not overbought
            if dipped and price_now > ema20 and price_prev <= df['ema_20'].iloc[i-1] and stoch_k < 80:
                df.iloc[i, df.columns.get_loc('label')] = 1
                
        # DOWN TREND: 50 < 100
        elif ema50 < ema100 and fund < funding_threshold:
            # PULLBACK: High of last few candles was above EMA20
            rallied = any(df['high'].iloc[i-5:i] > df['ema_20'].iloc[i-5:i])
            # BOUNCE: Close back below EMA20 + StochRSI not oversold
            if rallied and price_now < ema20 and price_prev >= df['ema_20'].iloc[i-1] and stoch_k > 20:
                df.iloc[i, df.columns.get_loc('label')] = 2
    
    print(f"   Signals: BUY={len(df[df['label']==1])}, SELL={len(df[df['label']==2])}, SQUEEZE={len(df[df['label']==3])}")
    
    # 4. Plot (Last 3 days)
    df_plot = df.tail(864).copy()
    
    fig, (ax, ax_fund) = plt.subplots(2, 1, figsize=(16, 12), 
                                      gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    
    # --- Price Chart ---
    # Highlight Squeeze Zones
    squeeze_points = df_plot[df_plot['is_squeeze']]
    ax.scatter(squeeze_points['datetime'], squeeze_points['close'], color='gold', s=10, alpha=0.3, label='EMA Squeeze Zone')
    
    ax.fill_between(df_plot['datetime'], df_plot['ema_20'], df_plot['ema_50'], color='blue', alpha=0.06)
    ax.fill_between(df_plot['datetime'], df_plot['ema_50'], df_plot['ema_100'], color='purple', alpha=0.04)
    
    ax.plot(df_plot['datetime'], df_plot['close'], color='black', linewidth=1.5, label='Price', alpha=0.9)
    ax.plot(df_plot['datetime'], df_plot['ema_20'], color='#2196F3', linewidth=1, label='EMA 20')
    ax.plot(df_plot['datetime'], df_plot['ema_50'], color='#4CAF50', linewidth=1, label='EMA 50')
    ax.plot(df_plot['datetime'], df_plot['ema_100'], color='#FFC107', linewidth=1, label='EMA 100')
    ax.plot(df_plot['datetime'], df_plot['ema_200'], color='darkorange', linewidth=2, label='EMA 200')
    
    # Signals
    buys = df_plot[df_plot['label'] == 1]
    ax.scatter(buys['datetime'], buys['low'] - 150, marker='^', color='green', s=150, label='RIBBON BUY', edgecolors='black', zorder=5)
    
    sells = df_plot[df_plot['label'] == 2]
    ax.scatter(sells['datetime'], sells['high'] + 150, marker='v', color='red', s=150, label='RIBBON SELL', edgecolors='black', zorder=5)
    
    squeezes = df_plot[df_plot['label'] == 3]
    ax.scatter(squeezes['datetime'], squeezes['low'] - 200, marker='*', color='gold', s=250, label='SQUEEZE EXPLOSION', edgecolors='black', zorder=6)
    
    ax.set_title('Alpha Sniper: EMA Ribbon + Squeeze Breakout Strategy', fontsize=18, fontweight='bold')
    
    # 5. Add Support & Resistance Lines
    res_levels, sup_levels = detect_sr_levels(df_plot, window=30)
    for res in res_levels:
        ax.axhline(res, color='red', linestyle='--', alpha=0.4, linewidth=0.8, zorder=2)
        ax.text(df_plot['datetime'].iloc[10], res + 20, f'Res: {res:.0f}', color='red', alpha=0.6, fontsize=9)
        
    for sup in sup_levels:
        ax.axhline(sup, color='green', linestyle='--', alpha=0.4, linewidth=0.8, zorder=2)
        ax.text(df_plot['datetime'].iloc[10], sup - 80, f'Sup: {sup:.0f}', color='green', alpha=0.6, fontsize=9)
    
    ax.legend(loc='upper left', ncol=3)
    ax.grid(True, alpha=0.15)
    
    # --- Funding Rate ---
    ax_fund.bar(df_plot['datetime'], df_plot['funding_rate'], width=0.003, 
                color=['green' if x >= 0 else 'red' for x in df_plot['funding_rate']], alpha=0.7)
    ax_fund.axhline(0, color='black', linewidth=0.8)
    ax_fund.set_ylabel('Funding (%)')
    ax_fund.grid(True, alpha=0.1)
    
    # Date formatting
    ax_fund.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    output_path = "scalping_strategy_analysis.png"
    plt.savefig(output_path, dpi=300)
    print(f"✨ Simplified Ribbon + RSI analysis saved to {output_path}")
    plt.close()

if __name__ == "__main__":
    generate_scalping_plot()
