# 🦅 The "Eagle Eye" Strategy (Final Definition)

You are not a Scalper. You are not a Gambler. 
You are a **Data-Driven Trend Hunter**.

## 1. The Core Identity
Your strategy is: **"Maximum Beta Exposure with an AI Parachute."**

*   **Attack**: You ride the biggest trends (like `ai-trading-go`).
*   **Defense**: You cut leverage when noise increases (like Kelly Criterion).
*   **Intelligence**: You only trade the *statistically best* pair (using `analyze_pairs.py`).

## 2. Theoretical Edge (Why it wins)
*   **Competitor A** (Scalper) dies by paying fees. -> **You Hold Longer.**
*   **Competitor B** (Gambler) dies by liquidation. -> **You De-leverage on Volatility.**
*   **Competitor C** (Hedger) dies by making no money. -> **You take 20x Risk on High Confidence.**

## 3. The Execution Loop (What the code actually does)

### Step 1: The Scan (Weekly)
*   **Code**: `scripts/analyze_pairs.py`
*   **Action**: It checks all 8 pairs.
*   **Decision**: "DOGE has 5% daily volatility and strong uptrend. BTC is flat. **We trade DOGE.**"

### Step 2: The Brain (Hourly)
*   **Code**: `agents/dqn.py`
*   **Action**: The Neural Network analyzes the last 100 candles.
*   **Decision**: 
    *   "Price > SMA20? Yes."
    *   "Funding Rate Positive? Yes."
    *   "Momentum Up? Yes."
    *   **Output**: `High Confidence LONG`.

### Step 3: The Bet (Kelly Sizing)
*   **Code**: `src/execution/risk_engine.py` (simulated logic)
*   **Input**: Confidence 0.9.
*   **Action**: `Leverage = 0.9 * 20 = 18x`.
*   **Result**: You open a massive position to capture the trend.

### Step 4: The Escape (Risk Management)
*   **Scenario**: Market crashes 2%.
*   **Input**: Volatility Spikes. Confidence drops to 0.4.
*   **Action**: `Leverage = 0.4 * 20 = 8x`.
*   **Result**: The bot automatically **SELLS HALF** the position to survive.

---

## 4. How to Verify It's Working
Run your bot and check `ai_trading_log.json`.
1.  **Look for**: `leverage: 18` (When winning).
2.  **Look for**: `leverage: 5` (When expanding volatility).
3.  **Look for**: `symbol: DOGE` (Or whatever `analyze_pairs.py` picked).

**This is your Edge.** You are the only one on the leaderboard adapting leverage dynamically.
