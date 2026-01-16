
# 🧠 FINAL SYSTEM: Perp-Aware Adaptive AI Trading Engine (PAAT-E)

Think of this as **AI controlling trading**, not AI replacing trading.

---

## 🔷 SYSTEM OVERVIEW (ONE SCREEN MENTAL MODEL)

```
Live Market Data (Perps)
   │
   ▼
[1] AI Regime Classifier  ← ML
   │  (What market am I in?)
   ▼
[2] AI Capital Allocator ← Bayesian / RL-lite
   │  (How much risk right now?)
   ▼
[3] Strategy Modules     ← Funding + Momentum
   │  (What trades exist?)
   ▼
[4] Risk Governor        ← Hard constraints
   │  (Can I survive this?)
   ▼
[5] Execution + AI Logs
```

This is **exactly** how professional systems are structured.

---

# 1️⃣ AI REGIME CLASSIFIER (REAL AI, FIRST PRIORITY)

### 🎯 Purpose

Detect **market state**, not price direction.

### 📥 Inputs (features)

Use only things perps care about:

* funding rate (t, t-1, t-2…)
* funding acceleration
* open interest % change
* realized volatility
* perp–spot basis
* liquidation spikes (proxy)

### 📤 Output

Probabilities (not labels):

```json
{
  "calm": 0.12,
  "crowded_longs": 0.63,
  "crowded_shorts": 0.18,
  "liquidation_risk": 0.07
}
```

### 🤖 Model choices (pick ONE)

* **HMM** (Hidden Markov Model) → best for regime switching
* Gaussian Mixture Model
* Temporal CNN
* LSTM classifier (small)

👉 HMM is PERFECT here:

* interpretable
* fast
* low data requirement
* judges understand it

This is **real AI**, not rules.

---

# 2️⃣ AI CAPITAL ALLOCATOR (THIS IS THE “SMART” PART)

This decides:

* position size
* leverage
* whether to trade at all

### 🎯 Purpose

Avoid blowing up during bad regimes.

### 📥 Inputs

* regime probabilities
* recent drawdown
* volatility
* funding strength
* liquidation risk score

### 📤 Output

Continuous decisions:

```json
{
  "risk_budget": 0.35,
  "max_leverage": 6,
  "trade_allowed": true
}
```

### 🤖 Model options

* **Bayesian Optimization** (recommended)
* Contextual Bandit
* Constrained Policy Gradient (lite RL)

Bayesian Opt is perfect because:

* small data
* adapts online
* stable
* judges LOVE it

This is **AI deciding risk**, which is very high signal.

---

# 3️⃣ STRATEGY MODULES (CONTROLLED BY AI)

These do NOT decide risk — they only propose trades.

---

## 🟢 Strategy A: Funding-Aware Directional Trading (CORE)

This is NOT pure funding arb — that’s too dangerous.

### Logic

* If funding very negative → long bias
* If funding very positive → short bias
* BUT only trade if:

  * price confirms
  * volatility acceptable
  * regime allows

### AI role

* AI decides:

  * size
  * leverage
  * whether signal is allowed

### Why this wins

* Funding gives edge
* Price confirmation reduces liquidation risk
* Works in live markets

---

## 🔵 Strategy B: Momentum (OPTIONAL, SMALL SIZE)

* Trend-following on perps
* Only enabled when:

  * regime confidence > threshold
  * funding not extreme
* Size capped by AI allocator

This is **secondary alpha**, not main engine.

---

# 4️⃣ RISK GOVERNOR (NON-AI, NON-NEGOTIABLE)

This layer **overrides everything**, including AI.

### Hard rules

* Max loss per trade: **≤1–2%**
* Max leverage:

  * Calm: ≤8×
  * Crowded: ≤4×
  * Liquidation risk: **0×**
* If drawdown >10% → halve risk
* If drawdown >15% → stop trading

This is what keeps you alive.

Judges LOVE seeing this.

---

# 5️⃣ EXECUTION + AI LOGGING (JUDGE GOLD)

Every decision must be logged.

### Example log

```json
{
  "timestamp": 1705593600,
  "symbol": "SOLUSDT",
  "regime_probs": {
    "crowded_shorts": 0.71
  },
  "strategy": "funding_directional",
  "action": "LONG",
  "leverage": 5,
  "position_size": 0.32,
  "funding_rate": -0.0016,
  "risk_budget": 0.35,
  "reasoning": [
    "negative funding",
    "OI stable",
    "low liquidation risk"
  ]
}
```

This screams **AI system**, not rule bot.

---

# 🛠️ BUILD ORDER (THIS MATTERS)

### Days 1–2

* Data pipeline
* Funding + OI + price
* Regime classifier (HMM)

### Days 3–4

* Capital allocator (Bayesian Opt)
* Risk governor

### Days 5–6

* Funding-aware strategy
* Execution engine
* AI logger

### Days 7–8

* Backtests
* Stress tests
* Kill-switch tests

### Days 9–10

* EC2 deployment
* API test
* Dry run

This is realistic.

---

# 🏁 WHY THIS CAN WIN FINALS

* Most teams: momentum-only → blow up
* Some teams: pure RL → unstable
* You: **AI-controlled risk + perp-aware logic**

Judges will see:

* real AI usage
* interpretable decisions
* safe deployment
* actual profit

That’s what WEEX wants to incubate.

---

## 🔥 NEXT STEP (YOUR MOVE)

Tell me ONE thing you want next:

1. Exact **HMM feature set + code**
2. Bayesian capital allocator implementation
3. Funding-aware strategy logic
4. Full repo structure
5. Judge-facing explanation doc

Pick one. We go deep.
