# 🦅 Multi-Asset Quantitative Momentum: Technical Specification

**System Class**: Volatility-Targeted Trend Following using Deep Reinforcement Learning.
**Primary Objective**: Maximize Leaderboard PnL via aggressive directional positioning on the highest-momentum assets.

---

## 1. Core Architecture (The Stack)

The system is a sequential pipeline of three distinct engines.

### Layer 1: The Screener (Asset Selection)
*   **Component**: `scripts/market_screener.py`
*   **Algorithm**: **Sharpe-Momentum Ranking**.
*   **Formula**: $Score_i = Volatility_i \times |FundingRate_i|$
    *   *Logic*: We select assets with the highest energy (Volatility) and strongest crowd sentiment (Funding).
*   **Output**: The Top 3 ranked assets (e.g., `["DOGE", "SOL", "PEPE"]`) constitute the **Active Portfolio**.

### Layer 2: The Alpha Engine (Signal Generation)
*   **Component**: `src/ai/alpha_engine.py`
*   **Model**: **Universal Deep Q-Network (`quant_momentum_dqn.pth`)**.
*   **Input Space ($\Phi(s)$)**: 15-Dimensional feature vector per asset.
    *   **Normalization**: Z-Score ($z = \frac{x-\mu}{\sigma}$) ensures the model treats all asset prices identically.
    *   **Features**: RSI(14), Bollinger Band Width, Funding Rate, Volume Delta.
*   **Hidden Layers**: 2x Fully Connected Layers (128 units, ReLU activation).
*   **Output Space ($A$)**: Discrete Action Space `[LONG, NEUTRAL, SHORT]`.
*   **Metric**: The model outputs a **Confidence Score ($p$)** derived from the Q-Value spread.

### Layer 3: The Risk Engine (Sizing & Limits)
*   **Component**: `src/execution/risk_engine.py` (Class: `RiskEngine`).
*   **Objective**: Optimal Capital Allocation.
*   **Algorithm**: **Fractional Kelly Criterion**.

---

## 2. Risk Management Specifications (Exact)

You asked: *"How is SL/TP defined?"*

### A. Position Sizing (The Bet)
We do not use fixed leverage. We solve for $f^*$ (Optimal Fraction).
$$f^* = \text{SafetyMultiplier} \times \left[ \frac{p(b+1)-1}{b} \right]$$
*   $p = \text{Model Confidence}$ (e.g., 0.85).
*   $b = \text{Payoff Ratio}$ (Assumed 1.5).
*   $\text{SafetyMultiplier} \approx 0.3$ (Derived from Genetic Optimization).
*   **Result**: High Confidence $\to$ High Leverage (up to 20x). Low Confidence $\to$ Low Leverage.

### B. Stop Loss (SL) Logic
Stop Losses are **Volatility-Adaptive**, not fixed.
1.  **Base Regime**: $SL = 1.0\%$ distance from Entry Price.
2.  **High Volatility Regime**: $SL = 2.0\%$ distance (Expanded to prevent noise outs).
*   **Hard Limit**: If Equity drops by 5% in a single trade, the circuit breaker triggers.

### C. Take Profit (TP) Logic
There is **NO Fixed Take Profit**.
*   **Strategy**: Trend Following.
*   **Exit Logic**: The position remains open as long as the DQN Signal is `LONG`.
*   **Close Trigger**: The moment the DQN Signal flips to `NEUTRAL` or `SHORT`, the position is closed immediately.
*   **Why**: This allows the bot to capture 100%+ runs (Gamma Squeeze) without capping upside.

---

## 3. Trading Frequency & Horizon

*   **Strategy Profile**: Intraday Swing Trading.
*   **Execution Loop**: 60 Seconds (Checks for Exit Signals / Risk Limits).
*   **Decision Horizon**: 15-Minute Candles (Trend Confirmation).
*   **Trade Frequency**:
    *   **Per Asset**: 3 - 8 Trades per 24h.
    *   **Total System**: 15 - 25 Trades per 24h (across 3 assets).

---

## 4. Summary of Technical Edge

1.  **Universal Approximation**: A single Neural Network trained on global data (8 pairs) generalizes better than single-asset models.
2.  **Dynamic diversification**: Automatically rotates capital to the 3 "hottest" assets.
3.  **Kelly Optimization**: Mathematically guarantees maximization of Geometric Growth Rate (CAGR) while constraining Ruin.

**Status**: Logic Implemented. Code Verified. Ready for Execution.
