import pandas as pd
import numpy as np
import os
import glob

def analyze_pairs(data_dir="data"):
    """
    Analyzes all CSVs in data_dir and ranks them by 'Investability'.
    """
    files = glob.glob(os.path.join(data_dir, "weex_data_*.csv"))
    if not files:
        # Try just *.csv if named differently
        files = glob.glob(os.path.join(data_dir, "*.csv"))
        
    results = []
    
    print(f"Analyzing {len(files)} pairs...")
    
    for f in files:
        symbol = os.path.basename(f).replace(".csv", "").replace("weex_data_", "")
        try:
            df = pd.read_csv(f)
            if len(df) < 100: continue
            
            # 1. Volatility (Hourly)
            df['returns'] = df['close'].pct_change()
            volatility = df['returns'].std() * np.sqrt(4) * 100 # Hourly % Vol
            
            # 2. Funding Rate Analysis
            # Assuming 'fundingRate' column exists (if fetched properly or mocked)
            # If not, we skip funding stats
            funding_yield = 0
            if 'fundingRate' in df.columns:
                funding_yield = df['fundingRate'].abs().mean() * 3 * 365 * 100 # Annualized Abs Yield
            
            # 3. Liquidity/Volume (Proxy)
            avg_volume = df['vol'].mean()
            
            # 4. Score (Simple Heuristic for Hackathon)
            # We want High Volatility (for price action) OR High Funding (for yield)
            # Score = Volatility + (Funding * 2)
            score = volatility + (funding_yield / 10) 
            
            results.append({
                "Symbol": symbol,
                "Volatility_1H": volatility,
                "Ann_Funding_Yield": funding_yield,
                "Avg_Volume": avg_volume,
                "Score": score
            })
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            
    # Convert to DF
    res_df = pd.read_json(pd.DataFrame(results).to_json()) # Clean types
    if res_df.empty:
        print("No valid data found.")
        return

    # Rank
    res_df = res_df.sort_values("Score", ascending=False)
    
    print("\n" + "="*50)
    print("🏆 PAIR RANKINGS (Data-Driven)")
    print("="*50)
    print(res_df.to_string(index=False))
    print("="*50 + "\n")
    
    # Select Top 3
    top_picks = res_df.head(3)
    symbols = top_picks['Symbol'].tolist()
    
    print(f"🔥 TOP 3 PORTFOLIO: {symbols}")
    
    # Save for Main Bot
    import json
    with open("active_portfolio.json", "w") as f:
        json.dump({"active_pairs": symbols}, f)
        
    print("✅ Portfolio saved to 'active_portfolio.json'")

if __name__ == "__main__":
    analyze_pairs()
