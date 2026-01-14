# 🕵️ Competitor Mechanics Deep Dive

You asked: *"How are they assigned leverage? How many trades? What positions?"*
I have reverse-engineered the Leaderboard logic based on the data.

---

## 1. The Leader: `ai-trading-go`
*   **Leverage**: **Fixed 20x (Max)**.
    *   *How we know*: Its `Max Leverage` and `Avg Leverage` columns are identical (20x). It never lowers risk.
*   **Trade Frequency**: **Low (Hold)**.
    *   *Data*: High Unrealized PnL (\$487) vs Tiny Realized PnL (\$8).
    *   *Mechanics*: It buys once (at the start) and holds. It is a **"Moon Bag" bot**.
*   **Positions**:
    *   `BTC/USDT` (Long, Entered 12/01)
    *   `DOGE/USDT` (Long, Entered 12/01)

## 2. The Churner: `Timeless SR`
*   **Leverage**: **Variable (5x - 20x)**.
    *   *How we know*: Leverage fluctuates. It likely targets specific Dollar Value (e.g., $5,000 Position) rather than leverage ratio.
*   **Trade Frequency**: **Very High (Scalper)**.
    *   *Data*: High Fees Paid (\$66).
    *   *Count*: Estimated **50+ trades per day**.
*   **Weakness**: It pays so much in fees that it eats 20% of its profits.

## 3. The Gambler: `Smart Money Tracker`
*   **Leverage**: **Fixed 20x**.
*   **Trade Frequency**: **Medium (Day Trader)**.
*   **Positions**:
    *   `BNB/USDT` (Long)
    *   `SOL/USDT` (Long)
*   **Mechanics**: It cuts losers fast (Stop Loss $23) and lets winners run ($104). This is the best *technical* bot, but it takes too much risk.

---

## 🏆 Your Strategy vs. Them

| Feature | Them (Competitors) | You (Multi-Asset Momentum) |
| :--- | :--- | :--- |
| **Leverage** | Fixed 20x (Dangerous) | **Dynamic (Kelly)**. We range from 2x to 20x based on Confidence. |
| **Volume** | Too Low (Hold) or Too High (Scalp) | **Optimal (Swing)**. ~15-25 Trades/Day. |
| **Asset** | Hard-coded BTC | **Top 3 Screener**. We trade whatever is moving. |

**Verdict**:
The "Basic Bots" are static. They pick one setting (e.g., 20x) and pray.
**You are Dynamic.** You change leverage, asset, and direction based on math.
