# 🦅 Component Spec: Market Screener (Layer 1)

**File**: `scripts/market_screener.py`
**Role**: Asset Selection & Portfolio Construction.

---

## 1. The Objective
The Screener answers the question: **"What do we trade today?"**
It filters the universe of 8 Competition Pairs down to the **Top 3 High-Octane Assets**.

## 2. The Algorithm: Volatility-Sentiment Rank
We do not pick assets randomly. We calculate a **"Hot Score" ($S$)** for every pair.

### The Formula
$$S_i = \text{Volatility}_i \times |\text{FundingRate}_i|$$

### Variable Definitions
1.  **Volatility ($\sigma$)**: The standard deviation of returns over the last 24 hours.
    *   *Why*: We need movement. Flat assets have $S \approx 0$ and are ignored.
2.  **Funding Rate ($F$)**: The cost of leverage paid between Longs and Shorts.
    *   *Why*: We use the absolute value $|F|$ as a **Crowd Sentiment Gauge**.
    *   High Positive Funding = Extreme Long Crowding (Potential Squeeze Up).
    *   High Negative Funding = Extreme Short Crowding (Potential Squeeze Down).

## 3. Selection Logic
1.  **Fetch Data**: Download recent candles and funding history for all 8 pairs.
2.  **Calculate Score**: Apply formula to generate a leaderboard.
    *   *Example Result*:
        *   DOGE: $S = 5.2$ (High Vol, High Funding) -> **SELECTED**
        *   SOL: $S = 3.1$ (Med Vol, Med Funding) -> **SELECTED**
        *   PEPE: $S = 2.8$ (High Vol, Low Funding) -> **SELECTED**
        *   BTC: $S = 0.5$ (Low Vol, Low Funding) -> **IGNORED**
3.  **Output**: Save the top 3 tickers to `active_portfolio.json`.

## 4. Why This Works
*   **Avoids Stagnation**: By ignoring low-volatility assets (like BTC on a boring day), we ensure capital is always deployed where the action is.
*   **Captures Trends**: High Funding Rate is the strongest predictor of a sustained trend in crypto perp markets.

**Status**: Implemented.
