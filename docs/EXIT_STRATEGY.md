# Exit Strategy Guide: Maximizing Profits on Perps

## 🎯 Objective
**Win the Hackathon**: Turn $1,000 into maximum profit in 2 weeks using BTC perpetual futures with 10x-20x leverage.

**Minimum Requirement**: 10 trades (bidirectional: LONG + SHORT).

---

## 🚨 Current Gap in the Bot

### What We Have ✅
1. **Entry Logic**: DQN decides LONG/SHORT based on 17 features.
2. **Position Sizing**: ATR-based (10% risk per trade).
3. **Hard Stop Loss**: 1.5x ATR distance (protects from liquidation).

### What's Missing ❌
**Exit Logic**: The bot currently has no intelligent exit mechanism. It either:
- Hits the stop loss (loses money), OR
- Holds forever (misses profit opportunities).

**This is critical** because with perps and leverage, **exit timing determines 80% of your profit**.

---

## 💡 The Three Exit Triggers

### 1. Take Profit (TP) - The Target 🎯

**Purpose**: Lock in gains when the trade moves in your favor.

**Options:**

#### A. Fixed Take Profit (Simple)
- **Rule**: Exit at +3% profit (2:1 risk/reward ratio).
- **Example**: 
  - Entry: $95,000
  - TP: $97,850
  - Stop: $93,575 (1.5% below)
  - Risk: $1,425 | Reward: $2,850

#### B. Trailing Take Profit (Advanced)
- **Rule**: Move TP up as price moves in your favor.
- **Example**:
  - Initial TP: +3%
  - If price hits +2%, move stop to breakeven.
  - If price hits +4%, move TP to +5%.
  - **Benefit**: Captures extended runs (5-10% moves).

---

### 2. Signal Reversal - The Flip 🔄

**Purpose**: Capture profits in BOTH directions (up and down).

**Rule**: If the DQN changes its signal, close the current position immediately.

**Examples:**

| Current Position | New DQN Signal | Action |
|-----------------|----------------|--------|
| LONG | SHORT | Close LONG → Open SHORT |
| LONG | HOLD | Close LONG → Wait |
| SHORT | LONG | Close SHORT → Open LONG |
| HOLD | LONG | Open LONG |

**Why This Works:**
- The DQN "sees" when momentum shifts (RSI flips, support breaks, etc.).
- Instead of riding the position down, you **flip** and profit from the reversal.
- **This is how you get 10+ trades in 2 weeks** (not just holding one position).

---

### 3. Time-Based Exit - The Timeout ⏱️

**Purpose**: Free up capital if a trade goes nowhere.

**Rule**: If position is open for 24-48 hours with no profit → Close it.

**Why This Matters:**
- **Opportunity Cost**: Your capital is locked in a dead trade.
- **Perps Funding**: You pay funding fees every 8 hours (can add up).
- **Better to exit flat** and wait for the next high-confidence signal.

---

## 🔥 The "Bidirectional Scalper" Strategy

### How to Hit 10+ Trades in 2 Weeks

**Current Setup (Passive):**
- Enter LONG → Hold → Exit (maybe 3-5 trades total).

**Aggressive Setup (Active):**
- Enter LONG → Exit at TP or Signal Flip → Enter SHORT → Exit → Repeat.

**Example 2-Week Timeline:**

| Day | Action | Trigger | Profit |
|-----|--------|---------|--------|
| 1 | LONG @ $95k | Support bounce | - |
| 2 | Exit @ $97.5k | TP +2.6% | +$260 |
| 3 | SHORT @ $97k | Resistance reject | - |
| 4 | Exit @ $94k | TP +3.1% | +$310 |
| 5 | LONG @ $93.5k | Support bounce | - |
| 6 | Exit @ $96k | TP +2.7% | +$270 |
| ... | Continue... | ... | ... |

**Result**: 10-15 trades, 60-70% win rate → **3-5x account growth**.

---

## ⚡ Implementation Options

### Option A: Quick Fix (Recommended for Now)

**Add to `main.py`:**
1. **Fixed Take Profit**: Exit at +3%.
2. **Signal Flip Detection**: If DQN action changes, close position.

**Pros:**
- Simple to code (5 minutes).
- Works immediately.
- Covers 80% of use cases.

**Cons:**
- Misses extended runs (5-10% moves).
- No partial exits.

---

### Option B: Advanced System (After Model Training)

**Add to `main.py`:**
1. **Trailing Stop**: Lock in profits as price moves.
2. **Partial Exits**: Take 50% profit at TP1, let 50% run to TP2.
3. **Volatility-Adjusted TP**: Use ATR to set dynamic targets.

**Pros:**
- Maximizes profit on big moves.
- More sophisticated (impresses judges).

**Cons:**
- More complex (15-20 minutes to implement).
- Needs backtesting to tune parameters.

---

## 🎯 Recommended Workflow

### Phase 1: Train the Model (NOW)
1. Upload code to Kaggle.
2. Run `WEEX_HACKATHON_TRAINING_NOTEBOOK.ipynb`.
3. Download `dqn_cmt_btcusdt.pth`.

### Phase 2: Add Exit Logic (AFTER Training)
1. Implement **Option A** (Quick Fix).
2. Test on paper trading for 24 hours.
3. If working well, add **Option B** features.

### Phase 3: Go Live
1. Deploy bot with real capital.
2. Monitor for 2-3 days.
3. Adjust TP/SL based on performance.

---

## 📊 Expected Performance

### Conservative Estimate
- **Trades**: 10-12 over 2 weeks.
- **Win Rate**: 60%.
- **Avg Profit per Win**: +3%.
- **Avg Loss per Loss**: -1.5%.
- **Net Result**: +12-18% → **$1,120-$1,180**.

### Aggressive Estimate (With Good Model)
- **Trades**: 15-20 over 2 weeks.
- **Win Rate**: 70%.
- **Avg Profit per Win**: +4%.
- **Avg Loss per Loss**: -1.5%.
- **Net Result**: +35-50% → **$1,350-$1,500**.

### Best Case (Catch a Trend)
- **Trades**: 8-10 over 2 weeks.
- **Win Rate**: 75%.
- **1-2 Big Wins**: +10-15% each.
- **Net Result**: +80-120% → **$1,800-$2,200**.

---

## 🚀 Next Steps

1. **Train the DQN model on Kaggle** (blocking everything else).
2. **Verify model works** (run inference test).
3. **Implement Quick Exit Logic** (Option A).
4. **Paper trade for 24 hours** (verify no bugs).
5. **Go live** and monitor.

**The code is 90% ready. We just need the brain file (`.pth`) to complete the system.**
