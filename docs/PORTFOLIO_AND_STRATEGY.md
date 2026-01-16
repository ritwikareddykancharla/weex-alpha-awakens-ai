# 💰 WEEX AI Wars: The $1,000 to Glory Portfolio Strategy

## 1. The Goal
**Objective**: Maximize Ending Balance.
**Starting Capital**: $1,000 USDT.
**Timeframe**: 2 Weeks.
**Constraints**: Max 20x Leverage. Min 10 trades per day.

---

## 2. Market Selection (The "Killing Fields")
We do NOT trade everything. We trade where the retail traders are gambling (and losing).

### Primary Pair: `cmt_dogeusdt` (DOGE/USDT)
*   **Why**: Highest retail interest = Most emotional trading = Predictable liquidations.
*   **Role**: **Aggressive Growth**. High volatility + liquidation cascades = Massive DQN rewards.

### Secondary Pair: `cmt_solusdt` (SOL/USDT)
*   **Why**: Strong funding rate volatility.
*   **Role**: **Yield Harvesting**. Great for Funding Rate Arbitrage.

### Anchor Pair: `cmt_btcusdt` (BTC/USDT)
*   **Why**: Stability.
*   **Role**: **Data Anchor**. We use BTC market sentiment to filter trades on DOGE/SOL (e.g., "Don't short DOGE if BTC is mooning").

---

## 3. Position Sizing & Smart Leverage (The "Multiplier")
We do NOT use fixed 20x leverage (that is suicide). We use **AI-Weighted Dynamic Leverage**.

**Formula**: `Position_Size = Account_Balance * Allocation_Size`
**Leverage**: Always 20x (Isolated), but on a *small chunk* of money.

| AI Confidence | Allocation % | Leverage | Effective Lev | Position Val ($1k Acc) | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **High (>80%)** | **35%** | **20x** | **7x** | $7,000 | Match the Leader (`ai-trading-go`). Aggressive but not suicide. |
| **Med (60-79%)** | **20%** | **20x** | **4x** | $4,000 | Standard Trend sizing. Safe from -20% crashes. |
| **Low (<60%)** | **0%** | **0x** | **0x** | $0 | Cash is King. |

**Why this is smarter**:
*   The "Dumb" Bot risks $1000 @ 20x = $20,000 Notional. A 5% drop wipes him out.
*   **You** risk $350 (35%) @ 20x = $7,000 Notional. A 5% drop loses you $350. **You survive.**

---

## 4. Risk Management (The "Survival Kit")
With 20x leverage, a 5% move against you = **Bankruptcy**.

1.  **Stop Loss**: Hard stop at **-1.5% Equity Loss** ($15).
    *   At 20x, this means if Price moves **0.075%** against us -> CUT IT.
    *   We scalp tiny moves. We don't hold bags.
    
2.  **Funding Escape**:
    *   If Funding Rate flips against us (we have to pay), close immediately unless profit > fee.

3.  **Black Swan Protocol**:
    *   If BTC drops > 3% in 15 mins -> **CLOSE ALL LONG POSITIONS**.

---

## 5. Execution Workflow (Your Daily Routine)

1.  **Data Heist (EC2)**: Run `scripts/fetch_training_data.py` to get fresh market insight.
2.  **Brain Training (Kaggle)**: Retrain `agents/dqn.py` every ~3 days to adapt to new "meta".
3.  **Deployment (EC2)**: Run `python -m src.main`.
    *   The bot handles the 24/7 scanning.
    *   It will execute trades automatically based on the table above.

---

## 6. Where are the Guides?

*   **EC2 <-> Kaggle Workflow**: [EC2_KAGGLE_WORKFLOW.md](file:///c:/Users/hp/.gemini/antigravity/brain/8c2e0142-5002-400b-ba0f-0a3e8bdeb28c/EC2_KAGGLE_WORKFLOW.md)
*   **Code Implementation**:
    *   **Bot Logic**: `src/main.py`
    *   **AI Brain**: `agents/dqn.py`
    *   **Simulation**: `scripts/backtest_strategy.py`
