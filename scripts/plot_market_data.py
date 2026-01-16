
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
import yfinance as yf



# Set Style for "Beautiful Plots" (Light Theme)
sns.set_theme(style="whitegrid", context="paper") # 'paper' context for smaller fonts in grid

# Colors (Professional Palette)
BTC_COLOR = '#F7931A' 
ETH_COLOR = '#627EEA'
SMA_COLOR = '#333333'
FILL_COLOR = '#E8F4FF'

def plot_market_data():
    # Load 60-Day YFinance Data
    btc_path = "data/yfinance_btc_15m.csv"
    eth_path = "data/yfinance_eth_15m.csv"
    
    if not os.path.exists(btc_path) or not os.path.exists(eth_path):
        print("❌ Data files not found. Run fetch logic first.")
        return

    df_btc = pd.read_csv(btc_path)
    df_eth = pd.read_csv(eth_path)

    # Convert timestamps
    # YFinance already has 'datetime' string (e.g. 2025-01-01 12:00:00+00:00)
    df_btc['time'] = pd.to_datetime(df_btc['datetime'])
    df_eth['time'] = pd.to_datetime(df_eth['datetime'])

    # Create Figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    fig.suptitle('Crypto Market Trend (Last 60 Days - 15m)', fontsize=24, fontweight='bold', color='#333333')

    # Plot BTC
    sns.lineplot(data=df_btc, x='time', y='close', ax=ax1, color=BTC_COLOR, linewidth=1.5, label='BTC Price')
    ax1.set_ylabel('BTC USD', fontsize=12, fontweight='bold')
    ax1.set_title("Bitcoin (BTC)", fontsize=16, loc='left')
    ax1.legend(loc='upper left', frameon=True)
    ax1.fill_between(df_btc['time'], df_btc['low'], df_btc['high'], color=BTC_COLOR, alpha=0.3)

    # Add SMA 200 (Major Trend) on 15m
    df_btc['sma_200'] = df_btc['close'].rolling(200).mean()
    ax1.plot(df_btc['time'], df_btc['sma_200'], color=SMA_COLOR, linestyle='-', alpha=0.8, linewidth=1.5, label='SMA 200 (Major Trend)')
    ax1.legend()
    
    # Plot ETH
    sns.lineplot(data=df_eth, x='time', y='close', ax=ax2, color=ETH_COLOR, linewidth=1.5, label='ETH Price')
    ax2.set_ylabel('ETH USD', fontsize=12, fontweight='bold')
    ax2.set_title("Ethereum (ETH)", fontsize=16, loc='left')
    ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper left', frameon=True)
    ax2.fill_between(df_eth['time'], df_eth['low'], df_eth['high'], color=ETH_COLOR, alpha=0.3)

    # Add SMA 200
    df_eth['sma_200'] = df_eth['close'].rolling(200).mean()
    ax2.plot(df_eth['time'], df_eth['sma_200'], color=SMA_COLOR, linestyle='-', alpha=0.8, linewidth=1.5, label='SMA 200')
    ax2.legend()

    # Beauty Grids
    ax1.grid(True, linestyle='-', alpha=0.4, color='#999999')
    ax2.grid(True, linestyle='-', alpha=0.4, color='#999999')

    # Remove spines
    sns.despine(left=True, bottom=True)

    plt.tight_layout()
    
    # Save
    output_path = "market_trend_60d.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✨ 60-Day Trend Plot saved to {output_path}")





def plot_ta_analysis():
    # Fetch 15m Data specifically for this view
    print("🚀 Fetching 15m Data for Last 2 Days...")
    pairs = {"BTC": "BTC-USD", "ETH": "ETH-USD"}
    data = {}
    
    for name, ticker in pairs.items():
        # yfinance allows 60d for 15m, so 2d is fine
        df = yf.download(ticker, period="2d", interval="15m", progress=False)
        if df.empty: continue
        
        # Clean Columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        df.columns = [str(c).lower() for c in df.columns] 
        df['time'] = pd.to_datetime(df['datetime']) 
        data[name] = df

    # Create Figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)
    fig.suptitle('Technical Analysis (Last 48 Hours - 15m Candles)', fontsize=24, fontweight='bold', color='#333333')

    # Helper to plot
    def plot_asset(ax, df, name, color):
        # Calculate Indicators
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['sma_50'] = df['close'].rolling(50).mean() 
        
        # Plot Price (Lighter Line)
        sns.lineplot(data=df, x='time', y='close', ax=ax, color=color, linewidth=1.0, alpha=0.8, label=f'{name} Price')
        
        # High/Low Shading (Darker as requested)
        ax.fill_between(df['time'], df['low'], df['high'], color=color, alpha=0.4)

        # Plot EMAs
        ax.plot(df['time'], df['ema_12'], color='#00CC99', linewidth=1.0, alpha=0.7, label='EMA 12 (Fast)')
        ax.plot(df['time'], df['ema_26'], color='#FF3366', linewidth=1.0, alpha=0.7, label='EMA 26 (Slow)')
        ax.plot(df['time'], df['sma_50'], color='#666666', linestyle='--', linewidth=1.0, alpha=0.7, label='SMA 50 (Trend)')
        
        # Fill Clouds
        ax.fill_between(df['time'], df['ema_12'], df['ema_26'], 
                        where=(df['ema_12'] >= df['ema_26']), color='#00CC99', alpha=0.2, interpolate=True)
        ax.fill_between(df['time'], df['ema_12'], df['ema_26'], 
                        where=(df['ema_12'] < df['ema_26']), color='#FF3366', alpha=0.2, interpolate=True)

        # Styling
        ax.set_ylabel(f'{name} USD', fontsize=12, fontweight='bold')
        ax.set_title(f"{name} Trend Analysis", fontsize=16, loc='left')
        ax.legend(loc='upper left', frameon=True)
        ax.grid(True, linestyle='-', alpha=0.35)

    if 'BTC' in data: plot_asset(ax1, data['BTC'], "Bitcoin", BTC_COLOR)
    if 'ETH' in data: plot_asset(ax2, data['ETH'], "Ethereum", ETH_COLOR)

    ax2.set_xlabel('Date (UTC)', fontsize=12, fontweight='bold')
    # Set X-Axis format to show Hours since it's only 2 days
    import matplotlib.dates as mdates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d-%b'))

    sns.despine(left=True, bottom=True)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    output_path = "market_ta_2days_15m.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✨ TA Plot (2d/15m) saved to {output_path}")

if __name__ == "__main__":
    # plot_market_data() # Old function
    plot_ta_analysis()   # New function
