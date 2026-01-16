# 🛡️ Component Spec: Risk Engine (Layer 3)

**File**: `src/execution/risk_engine.py` (Class: `RiskEngine`)
**Role**: Capital Allocation & Survival.

---

## 1. The Objective
The Risk Engine answers the question: **"How much do we bet?"**
It acts as the constraint function, ensuring we maximize growth without exposing the account to Ruin Risk.

## 2. Algorithm 1: Fractional Kelly Criterion
We do not guess the leverage (e.g., "Always 20x"). We solve for it mathematically.

### The Formula
$$f^* = \lambda \times \left[ \frac{p(b+1)-1}{b} \right]$$

### Inputs
*   $p$ (**Probability**): The Confidence Score from the Alpha Engine (e.g., 0.82).
*   $b$ (**Odds**): The Payoff Ratio (Avg Win / Avg Loss). We assume conservative 1.5.
*   $\lambda$ (**Safety Fraction**): A dampener derived from Genetic Optimization (set to 0.3).

### Execution
*   **High Confidence (p=0.90)** $\rightarrow$ $f^*$ is high $\rightarrow$ **High Leverage (20x)**.
*   **Low Confidence (p=0.55)** $\rightarrow$ $f^*$ is low $\rightarrow$ **Low Leverage (2x)**.

*This allows the bot to "Strike Hard" when the setup is perfect, and "Play Defense" when it is weak.*

## 3. Algorithm 2: Adaptive Liquidation Prevention
The Risk Engine monitors market volatility in real-time ($V_{market}$).

### Dynamic Stop Loss
Instead of a static stop loss, we adapt to the "Noise Level".
1.  **Low Volatility**: Stop Loss = **1.0%** (Tight).
2.  **High Volatility**: Stop Loss = **2.0%** (Wide).
    *   *Why*: In a choppy market, a tight stop gets hit by random noise. We widen it to stay in the trade.

### The Circuit Breaker
*   **Hard Rule**: If daily drawdown hits **-15%**, the bot halts all trading for 4 hours.
*   **Why**: Prevents "Tilt" (Revenge Trading) during a market crash.

## 4. Why This Works
*   **Geometric Growth**: The Kelly Criterion is mathematically proven to generate the fastest wealth growth over time.
*   **Survival**: By cutting leverage when confidence is low, we avoid the heavy losses that bankrupt "Basic Bots".

**Status**: Implemented & Optimized.
