# 💸 Capital Flow Simulation: The $1,000 Journey

You asked: *"How is my $1000 allocated, monitored, and reallocated?"*
Here is a precise, second-by-second simulation of your money moving through the system.

---

## 🏛️ The Setup
*   **Account Balance**: `$1,000 USDT`
*   **Active Portfolio**: `DOGE`, `SOL`, `PEPE` (Selected by `market_screener.py`)

---

## ⏱️ Hour 0:00 - The Opportunity (Allocation)
**Event**: The Alpha Engine detects a **Long Signal** on **DOGE**.
*   **Signal**: `LONG`
*   **Confidence**: `0.80` (Very High)
*   **Volatility Regime**: `Low`

**Step 1: The Bet Size (Risk Engine)**
The `risk_engine.py` runs the Kelly Formula:
*   `Confidence 0.80` $\rightarrow$ Optimal Kelly Fraction is **28%**.
*   **Calculation**: $\$1,000 \times 0.28 = \$280$.

**Step 2: Execution (Main Loop)**
*   The bot sends an order to Weex: **Long $280 of DOGE**.
    *   *Leverage*: 20x Isolated.
    *   *Margin Used*: $\$14$ (The rest is reserve).
    *   *Position Size*: $\$280$ Notional.

**Status**:
*   **In Trade**: $280 (DOGE)
*   **Free Capital**: $720 (Waiting for SOL/PEPE)

---

## ⏱️ Hour 2:00 - The Monitor (PnL Check)
**Event**: DOGE Price drops by 1%.
*   **Current PnL**: -1% on 20x Leverage = **-20% ROE**.
*   **Net Loss**: $-\$2.80$.

**Step 3: The Watchdog (Position Manager)**
Every 60 seconds, `position_manager.py` runs `check_exit_conditions()`:
1.  **Check Stop Loss**: Is PnL < -2% (Equity)? No, it's small.
2.  **Check Signal**: Is Alpha Engine still Long?
    *   *AI Update*: "Confidence dropped to 0.40 (Neutral)".

**Step 4: The Exit (Reallocation)**
Because the AI Confidence died, the Position Manager **CLOSES** the trade immediately.
*   **Action**: Sell DOGE Market.
*   **Result**: You lost $2.80. You have **$997.20** back in cash.

---

## ⏱️ Hour 4:00 - The Reallocation (Recycling)
**Event**: PEPE starts pumping.
*   **Signal**: `LONG`
*   **Confidence**: `0.95` (Extremely High).

**Step 5: The New Bet**
Your capital was freed up from DOGE. Now it goes into PEPE.
*   `Confidence 0.95` $\rightarrow$ Kelly Fraction **35%**.
*   **Calculation**: $\$997.20 \times 0.35 = \$349$.

**Execution**:
*   The bot buys **$349 of PEPE**.
*   *Note*: If we hadn't closed DOGE, we might not have had enough "Safe Margin" for this big bet. This is **Reallocation**.

---

## 📊 Summary Logic

| Component | Code File | Role in this Story |
| :--- | :--- | :--- |
| **Allocator** | `risk_engine.py` | Calculated the $280 and $349 bet sizes. |
| **Monitor** | `position_manager.py` | Saw DOGE Signal fade and PnL drop. |
| **Executor** | `weex_client.py` | Clicked "Buy" and "Sell" buttons. |

### 📉 Trade Volume Answer
In this simulation:
*   **Trades**: 2 (DOGE Buy/Sell, PEPE Buy).
*   **Time**: 4 Hours.
*   **Daily Projection**: If this pace continues, you will see **~12 Trades per day**.

**This is how the machine works.** It flows water (money) from dead plants (losers) to growing trees (winners).
