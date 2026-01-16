# 🧠 WEEX AI Wars: Strategy & Training Guide

## 1. The Strategy: Smart Trend Following (DQN)

### The "Alpha"
You noticed the Leaderboard: The winners are **Directional Trend Followers**. They buy and hold.
WEEX allows 20x leverage. In a Bull Run, **Trend Following > Arbitrage**.

**Our Twist: The "Funding-Aware" Trend Follower.**
Most bots just look at Price. We look at **Price + Sentiment (Funding Rate)**.
*   **Rationale**: High Funding Rate means the crowd is Bullish.
*   **Our Move**: If Price is Up AND Funding is Positive -> **We go Aggressive Long (20x)**.
*   **The Edge**: We are surging *with* the crowd, but using the Funding Rate data to confirm it's a "Real Move" and not a fake-out.

### The AI Engine (Deep Q-Network)
 The DQN inputs 15 features to output a `Confidence Score`.
*   **Input**: Price Momentum (RSI), Volatility, **Funding Rate**.
*   **Logic**:
    *   If Trend is Strong + Paying fees is low -> **Long**.
    *   If Trend is Weak + Fees are high -> **Exit**.
*   **Output (Action)**:
    *   `LONG`: Ride the wave.
    *   `SHORT`: Hedge if data turns bearish.
*   **Reward Function**:
    *   Primary Reward: **Price Appreciation** (Capital Gains).
    *   Secondary Reward: **Funding Yield** (Bonus).
    *   Penalty: **Drawdown** (Don't hold bags).

    *   Penalty: **Drawdown** (Don't hold bags).

---

## 2. Portfolio Management (The Risk Engine)

### A. Dynamic Leverage (The "Kelly" Boost)
You asked about Leverage. We do NOT use fixed leverage (that's how you blow up).
We use **AI-Weighted Dynamic Leverage**:
*   **Confidence > 80%**: **15x - 20x Leverage**. (Sniper Mode).
*   **Confidence 60-79%**: **5x - 10x Leverage**. (Standard Trend).
*   **Confidence < 60%**: **1x or Cash**. (Defense).

*Result*: When the AI is "Sure" (like on Jan 12th), we hit hard. When it's noise, we stay safe.

### B. Multi-Pair Architecture
The bot is not stuck on one pair.
1.  **The Scanner (`analyze_pairs.py`)**:
    *   Runs everyday.
    *   Checks all 8 Competition Pairs (BTC, ETH, SOL, DOGE, etc.).
    *   **Selects**: The pair with the **Highest Volatility** (for movement) AND **Positive Funding** (for trend confirmation).
2.  **The Execution**:
    *   If DOGE is moving: We trade DOGE.
    *   If BTC is moving: We trade BTC.
    *   **We go where the action is.**

---

## 2. How to Train the Model

You cannot run an AI model without "teaching" it first. It starts knowing nothing (random guessing). Training is the process of letting it practice on historical data.

### Step-by-Step Training Instructions

#### **Step 1: Open Your Terminal**
Make sure you are in the project root: `c:\Users\hp\Desktop\weex-alpha-awakens-ai`

#### **Step 2: Run the Training Agent**
We have a prepared command that:
1.  Fetches the last 2 weeks of WEEX market data (15-minute candles).
2.  Runs the AI through this data 50 times (Epsiodes).
3.  Each time, it learns from its mistakes.
4.  Saves the "Brain" to `models/weex_dqn.pth`.

**Run this command:**
```powershell
.\.venv\Scripts\python agents/dqn.py
```

#### **Step 3: Verification**
Watch the terminal output. You want to see:
*   `Episode 1/50 ... Reward: -5.2 ...` (It starts stupid, losing money)
*   `Episode 25/50 ... Reward: 1.5 ...` (It starts learning)
*   `Episode 50/50 ... Reward: 12.8 ...` (It has learned a profitable strategy)

Once finished, check for the file: `models/weex_dqn.pth`.

---

## 3. How to Execute (Live/Simulation)

Once you have the `models/weex_dqn.pth` file:

**Run the Main Bot:**
```powershell
.\.venv\Scripts\python -m src.main
```
The bot will load `weex_dqn.pth` and start making decisions based on live WEEX market data using the strategy it learned.
