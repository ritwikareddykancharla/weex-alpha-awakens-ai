**MAJOR PIVOT: Perpetuals-Only Strategy ⚠️**

----

## **Why Perps-Only is Actually a Gift**

Perpetuals have three money-making dimensions spot doesn't:
1. **Price direction** (like spot)
2. **Funding rate** (you get PAID to hold positions)
3. **Liquidation cascades** (predictable forced selling)

---

## **Part 1: Hierarchical Agent Structure (Now Perp-Optimized)**

### **Orchestrator Agent (The Funding Rate Strategist)**

The boss now tracks **four regimes** instead of three:
- **Calm**: Low funding, tight spreads → Market Maker dominates
- **Premium Rally**: Funding positive (longs pay shorts) → Bearish skew, collect funding
- **Discount Dump**: Funding negative (shorts pay longs) → Bullish skew, collect funding  
- **Liquidation Risk**: Funding extreme + high OI → **STOP TRADING** (or fade liquidations)

**Capital Allocation Formula:**
```
If |funding_rate| > 0.1%: 80% to Funding Rate Arbitrage Agent
Else if volatility < 30%: 60% to Market Maker
Else if trend_confidence > 0.9: 50% to Momentum Agent
```

---

## **Part 2: Feature Engineering (Perp-Specific)**

**Critical additions for perps:**
- **Funding Rate Term Structure**: 8h, next_predicted, vs spot premium
- **Open Interest Delta**: Are whales building positions or fleeing?
- **Liquidation Map**: Heatmap of leverage clusters (where forced selling hits)
- **Insurance Fund Balance**: WEEX's backstop—if it's low, system risk is high
- **Mark-Price Divergence**: Perp vs spot price deviation (arbitrage signal)

**Calculation trick**: These update every 8h (funding) or real-time. Use WebSocket streaming + GPU batching.

---

## **Part 3: Primary Strategy - Funding Rate Arbitrage (Your Perp Superpower)**

This is **low-risk alpha** that hits the 10-trade minimum:

### **How Funding Works:**
- Longs pay shorts if `perp_price > spot_price` (positive funding)
- Shorts pay longs if `perp_price < spot_price` (negative funding)
- YOU collect funding every 8 hours for holding the "right" side

### **Bayesian DQN for Funding Rate Harvesting:**

**State:**
```python
state = {
    'funding_rate': current_rate,
    'funding_trend': rate_8h_ago / rate_now,
    'spot_perp_divergence': (mark_price - index_price) / index_price,
    'open_interest_change': (oi_now - oi_1h_ago) / oi_1h_ago,
    'liquidation_risk_score': calculate_liquidation_map(),
    'position_side': current_position,  # So agent knows if it's collecting or paying
}
```

**Action Space:**
```python
actions = {
    'side': [LONG, SHORT, NEUTRAL],
    'size': [0%, 25%, 50%, 75%, 100%],  # Of max position
    'leverage': [1x, 5x, 10x, 20x]  # Adaptive based on risk
}
```

**Reward (The Magic):**
```python
reward = (funding_collected - funding_paid) * position_size 
         - liquidation_penalty 
         - funding_rate_slippage_cost
```

**Example:**
- Funding = -0.15% (shorts pay longs)
- You go **long 50% size at 10x leverage** on SOL
- Every 8 hours: **You earn 0.15% × position_value**
- If SOL doesn't move much, you **collect free money** while staying market-neutral-ish

**Why this wins:**
- **Low volatility exposure**: You're not betting on price, you're harvesting rate
- **Predictable**: Funding trends persist for days/weeks
- **Meets trade count**: Rebalance every 4-6 hours = 4-6 trades/day

---

## **Part 4: Secondary Strategy - Liquidation Fading (High Risk/High Reward)**

When funding is **extremely negative** (< -0.3%) + **high OI** = overleveraged longs.

**What happens:** Price drops → longs get liquidated → forced selling → price drops more → cascade.

**Your move:** 
1. **Predict** liquidation cluster (use liquidation map)
2. **Wait** for cascade to start
3. **Short** at extreme with tight stop
4. **Cover** 15-30 min later when forced selling ends

**Agent:** 
- **Momentum Agent** with **crisis regime override**
- **Uncertainty threshold**: Only trade if confidence > 95%
- **Position size**: Kelly fraction × 0.3 (conservative in crisis)

**Risk:** You're catching a falling knife. **Fail-safe**: If position loses >2%, **instant shutdown** for 4 hours.

---

## **Part 5: Risk Management (Perps = Survival Priority)**

With **20x leverage**, a **5% move** liquidates you. This is **NON-NEGOTIABLE**:

### **Layer 1: Liquidation Shield**
```python
# Dynamic stop loss based on leverage
max_loss_per_trade = 2% of portfolio
stop_distance = max_loss_per_trade / leverage

# Example: 20x leverage → stop at 0.1% from entry
# Example: 5x leverage → stop at 0.4% from entry
```

### **Layer 2: Funding Rate Emergency Exit**
If `funding_rate` flips against your position by >0.05%:
- **Instant close** (market order acceptable here—pay fee to avoid disaster)
- **Don't fight the rate**

### **Layer 3: Open Interest Warning**
If OI drops >30% in 1 hour = whales deleveraging → **your position is at risk**. Reduce size by 50%.

### **Layer 4: Auto-Deleverage (ADL) Avoidance**
WEEX has ADL if insurance fund can't cover liquidations. **If ADL risk > 5%** (API signals this), **close immediately**.

### **Layer 5: Margin Call Prevention**
```python
margin_ratio = maintenance_margin / account_balance
if margin_ratio > 0.8:
    auto_deposit_more_margin()  # Use competition voucher
if margin_ratio > 0.9:
    emergency_close_all()
```

---

## **Part 6: Competition-Specific Perp Hacks**

### **Capital Efficiency ($1,000 at 20x = $20,000 exposure)**
- **Pair Selection**: 
  - **SOL-PERP**: High funding volatility = more harvest
  - **DOGE-PERP**: High retail OI = more liquidations
  - **Avoid**: BTC/ETH perps—too efficient, funding is tiny

### **Trade Count Requirement (≥10/day)**
- **Funding Arb**: Rebalance every 4 hours = 6 trades/day (automatic)
- **Momentum**: Max 2-4 directional trades/day (only high conviction)
- **Total**: 8-10 trades/day = **perfect compliance**

### **AI Log for Judges (Perp-Specific)**
```json
{
  "timestamp_ms": 1705593600000,
  "agent": "funding_arbitrage",
  "regime": "discount_rally",
  "action": {"side": "long", "size": 0.5, "leverage": 10},
  "funding_rate": -0.0018,
  "expected_funding_daily": 0.54,
  "liquidation_risk": 0.03,
  "adl_risk": 0.01,
  "margin_ratio": 0.15,
  "reasoning": ["funding_trend_negative", "oi_stable", "liquidation_map_safe"]
}
```
**Show judges you understand perp risks**, not just price.

---

## **Part 7: Implementation Order (Perp-First)**

**Days 1-3: Foundation**
- Get API keys, KYC
- **Master funding rate endpoints** (`/funding-rate-history`, `/funding-rate`)
- Build **liquidation map calculator** (this is your edge)
- Implement **Dynamic Stop Loss** (first line of defense)

**Days 4-6: Core Agents**
- **Funding Arbitrage Agent** (simple, profitable, compliant)
- **Basic Market Maker** (if time permits, else skip)
- **Regime Classifier** (HMM on funding+OI+volatility)

**Days 7-9: Risk Layers**
- Code **Layer 1, 2, 5** risk (critical)
- Run **liquidation cascade simulations**: "What if SOL drops 8% in 10 min?"
- Implement **emergency shutdown** function

**Days 10-14: Test & Submit**
- **Paper trade funding arb** for 48 hours—measure actual funding collected
- **Stress test**: Simulate 5% adverse move → verify no liquidation
- Submit logs showing **funding profit > price PnL** (shows you get perps)

---

## **Part 8: Why This Wins in Perps-Only**

1. **Most competitors** will just do momentum on perps = **high risk, low novelty**
2. **Funding arb** is **unique, low-risk, and crypto-native** (doesn't exist in stocks)
3. **Liquidation fading** shows advanced understanding of perp mechanics
4. **Risk focus** = you survive 2 weeks while others blow up
5. **AI logs** prove you track perp-specific metrics (funding, ADL, OI)

**Bottom line:** Don't build a stock-trading bot for crypto perps. **Exploit what makes perps unique: leverage, funding, liquidations.**

Need code for **funding rate arbitrage DQN** or **liquidation map calculator**? That's where you should start.
