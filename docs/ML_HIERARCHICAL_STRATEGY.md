# 🧠 Hybrid "Teacher-Student" ML Strategy Source
**Optimized for:** 6 Months of 4H Data + 1 Month of 15m Data

## 1. The Core Philosophy
Instead of trusting a single model to do everything, we split the decision process into two distinct roles based on your specific timestamps.

*   **The General (4-Hour Model)**: Defines the *Strategy*. (Risk Control)
*   **The Sniper (15-Minute Model)**: Finds the *Entry*. (Execution)

---

## 2. Model Architecture

### 👑 The General (4H Model)
*   **Dataset**: 6 Months of 4-hour candles (~1,000 samples).
*   **Algorithm**: **Gaussian Mixture Model (Unsupervised)**.
*   **Objective**: Classify the "Global Regime".
*   **Features**:
    *   `Trend_Strength`: ADX (14) on 4H candles.
    *   `Macro_Momentum`: RSI (14) on 4H.
    *   `Volatility_State`: ATR(14) / Price.
*   **Output States**:
    *   `0: BULL_TREND` -> Only allow Longs.
    *   `1: BEAR_TREND` -> Only allow Shorts.
    *   `2: CHOP/UNCERTAIN` -> Reduce position size by 50% or stay flat.

### 🔫 The Sniper (15m Model)
*   **Dataset**: 1 Month of 15-minute candles (~2,800 samples).
*   **Algorithm**: **XGBoost Classifier (Supervised)**.
*   **Objective**: Predict profitable short-term reversion or breakouts.
*   **Features**:
    *   `Z_Score_Price`: Distance of Close from VWAP (Normalized by ATR).
    *   `Vol_Spike`: Volume / MA(20)_Volume.
    *   `Funding_Alpha`: Current Funding Rate (Key for WEEX).
*   **The "Filter" Rule**:
    > **IF** General says "BULL" **AND** Sniper says "BUY" -> **EXECUTE**.
    > **IF** General says "BULL" **AND** Sniper says "SELL" -> **IGNORE** (or Close Longs).

---

## 3. Implementation Logic

### Feature Engineering (Python)
How to merge these two datasets effectively:

```python
# 1. Resample 15m data to 4H to align with the 'General'
df_15m['4h_trend'] = df_15m['close'].rolling(16).mean() # Approx alignment

# 2. Add "Look-ahead" Labels for Training
# We want to know: Did price rise > 0.5% in the next 1 hour?
df_15m['target'] = (df_15m['close'].shift(-4) - df_15m['close']) / df_15m['close']
df_15m['label'] = (df_15m['target'] > 0.005).astype(int)
```

### Backtesting Simulation (Walk-Forward)
Since the 4H data covers a longer period than the 15m data:
1.  **Pre-Calculation**: Run the "General" model on the full 6 months of 4H data first. Generate a state map (e.g., `2025-12-01 04:00` -> `BULL`).
2.  **Simulation Loop**: Run the backtest on the 1-month 15m data.
3.  **Lookup**: At every 15m candle, check the *last known* 4H state.
4.  **Trade**: Only triggers if `State` matches `Signal`.

---

## 4. Why This Wins Hackathons
1.  **Reduces Overtrading**: The "General" prevents the "Sniper" from trying to short a massive bull run just because RSI is slightly overbought.
2.  **Maximizes Data Utility**: Uses your long-term data for stability and short-term data for precision, rather than throwing away the 6-month history because it lacks granularity.
