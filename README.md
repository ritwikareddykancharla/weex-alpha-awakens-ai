# weex-alpha-awakens-ai

# 🧠 Multi-Strategy Quant Engine

This repository houses a **Quantitative Momentum Strategy** enhanced by Machine Learning (GMM + DQN) for the WEEX Global AI Trading Hackathon (Jan-Feb 2026).

### 📊 Core Strategies & Alpha Factors

1.  **Quantitative Momentum (DQN)**
    *   Utilizes a Deep Q-Network (Reinforcement Learning) to identify high-probability breakout setups across 8 concurrent assets.
    *   Filters momentum signals using volume-weighted verification to avoid false breakouts.

2.  **GMM Regime Classification**
    *   Deploys **Gaussian Mixture Models** to classify market states into "Trending", "Mean Reverting", or "Volatile".
    *   Dynamically switches strategy parameters (e.g., tightens Stop Loss in high volatility) based on the detected regime.

3.  **Dynamic Portfolio Allocation**
    *   Rejects static sizing. Uses **Kelly Criterion** estimation to optimally size bets based on model confidence.
    *   Real-time rebalancing via WebSocket data streams to capture alpha in microseconds.
# Advanced Strategy for WEEX AI Hackathon: Neuro-Symbolic Adaptive Market Engine

---

## **Core Architecture: Meta-Adaptive Multi-Agent System**

Instead of a monolithic model, implement a **decentralized AI architecture** that mirrors Web3 principles:

### **1. Hierarchical Agent Structure**

```python
# Simplified architecture concept
├── Orchestrator Agent (Meta-Learner)
│   ├── Regime Classifier (HMM-based)
│   └── Capital Allocator (Bayesian Optimization)
├── Execution Agents (3 specialized)
│   ├── Market Maker Agent (GAT + Deep Q-Learning)
│   ├── Momentum Agent (Temporal Fusion Transformer)
│   └── Arbitrage Agent (Graph Neural Network)
└ward Risk Layer (Ensemble uncertainty quantification)
```

**Key Innovation**: Each agent is a **separate Bayesian Neural Network** with MC Dropout for uncertainty-aware predictions. The Orchestrator uses meta-learning (MAML) to rapidly adapt agent weights based on 2-week performance.

---

## **2. Feature Engineering: Beyond Price Bars**

Don't use OHLCV. Build **microstructure features** that retail bots can't access:

```python
# Advanced feature set (calculate in C++/CUDA for speed)
- Order Flow Imbalance: (ΔBidVolume - ΔAskVolume) / (ΔTotalVolume)
- VPIN (Volume-Synchronized PIN): Toxic flow detection
- Quote Slope: dPrice/dDepth across order book levels
- Cross-Asset Lead-Lag: Graph attention networks on 8 pairs
- On-Chain Momentum: Exchange netflow velocity (via subgraph)
- Social Sentiment: Fine-tuned Llama on crypto Twitter/TG (run locally)
- Funding Rate Term Structure: Perpetual futures curve
- Liquidation Cluster Detection: Heatmap of clustered stops
```

**Implementation**: Use **RAPIDS (GPU pandas)** for feature calculation <10ms latency.

---

## **3. Primary Strategy: Adaptive Market Making with AI Inventory Control**

This is your **high-frequency, low-risk baseline** to stay profitable while meeting the 10-trade minimum.

### **Bayesian Deep Q-Learning for Spread Optimization**

```python
# State space (continuous)
state = {
    'inventory': current_position / max_position,
    'position_pnl': unrealized_pnl,
    'midprice_volatility': realized_vol_1m / realized_vol_5m,
    'order_book_imbalance': (bid_depth - ask_depth) / (bid_depth + ask_depth),
    'agent_uncertainty': mc_dropout_variance(predictions)
}

# Action space (discrete)
actions = {
    'spread_multiplier': [0.5, 1.0, 1.5, 2.0],  # relative to base spread
    'skew': [-0.5, 0, 0.5]  # bias quotes to offload inventory
}

# Reward (competition-optimized)
reward = realized_pnl - 2 * inventory_penalty - 0.5 * trade_count_penalty
```

**Innovation**: Use **Episodic Memory** (replay buffer with regime labels) to avoid catastrophic forgetting during the 2-week period.

---

## **4. Secondary Strategy: Regime-Switching Momentum Detection**

Your **alpha generator** for capitalizing on directional moves:

### **Temporal Fusion Transformer with Regime Conditioning**

```python
# Architecture
- Encoder: Multi-head attention on 8 pairs (cross-attention)
- Decoder: Autoregressive prediction with static covariates
- Regime Injection: Hidden state modulation via HMM regime embedding
- Uncertainty: Evidential Deep Learning (predicts parameters of distribution)

# Prediction target
Predicts the **conditional probability** of a >1% move in next 15m, 1h, 4h
Uncertainty > threshold → defer to Market Maker agent (risk-off)
```

**Key**: Only trade when **uncertainty is low** and **expected value > 2x VaR**.

---

## **5. Risk Management: 5-Layer Defense System**

Given 20x leverage and $1,000 capital, **survival is victory**.

### **Layer 1: Position-Level (Micro)**
- **Dynamic Stop-Loss**: ADX-based ATR trailing stop (not fixed %)
- **Take-Profit**: Partial scaling based on R-ratio (risk:reward > 2:1)

### **Layer 2: Portfolio-Level (Meso)**
- **Monte Carlo VaR**: 99% confidence, 1-day horizon, recompute every 5 minutes
- **Leverage Limiter**: `max_leverage = 20 * (1 - portfolio_var / var_threshold)`

### **Layer 3: Regime-Aware (Macro)**
- **Hidden Markov Model**: 3 regimes (Calm, Volatile, Crisis)
- In Crisis regime: **automatically halve position sizes, double spreads**

### **Layer 4: Adversarial Robustness**
- **Gradient-based Attack Simulation**: Test model against adversarial order book perturbations
- **Fuzzing**: Random API delays, partial fills → ensure graceful degradation

### **Layer 5: Meta-Risk Layer**
- **Kelly Criterion with Uncertainty**: `bet_size = kelly_fraction * (1 - uncertainty)`
- **Automatic Shutdown**: If drawdown >15% or VaR breach >3x → stop trading until manual review

---

## **6. Competition-Specific Optimizations**

### **Capital Efficiency (Critical for $1,000)**
- **Focus on mid-cap pairs**: SOL, ADA, DOGE have better volatility alpha than BTC/ETH
- **Avoid BNB**: Binance-related risks, lower volatility
- **Max 2-3 concurrent positions**: Prevent over-leverage

### **Trade Count Requirement (≥10 trades)**
- **Market Maker**: Generates 50-100 trades/day naturally
- **Minimum trade frequency**: Set agent to enforce at least 1 trade per 4 hours in quiet periods
- **Avoid wash trading**: Ensure each trade has genuine signal > noise threshold

### **AI Log Submission (Make or Break)**
Log **everything** in structured JSON for scoring:

```json
{
  "timestamp_ms": 1705593600000,
  "agent_id": "market_maker_01",
  "regime": "volatile",
  "action": {"spread": 1.5, "skew": -0.2},
  "uncertainty": 0.12,
  "position": {"symbol": "SOLUSDT", "size": 0.5, "side": "long"},
  "risk_metrics": {"var_99": 23.4, "margin_usage": 0.15},
  "features_snapshot": {"ofi": 0.34, "vpin": 0.12, ...},
  "reasoning_chain": ["Order book imbalance detected", "Uncertainty within threshold", "Executing quote update"]
}
```

**Key**: Include **interpretable reasoning** in logs for judge evaluation.

---

## **7. Implementation Roadmap (10 Days)**

### **Days 1-3: Foundation & API**
- [ ] Register UID, complete KYC, get API keys
- [ ] Set up AWS/GCP instance (use GPU credits from prize partners)
- [ ] Build **low-latency WebSocket connector** to WEEX (Python asyncio + uvloop)
- [ ] Implement **feature pipeline** with RAPIDS
- [ ] Get basic **Market Maker** running (even if static quotes)

### **Days 4-6: Core AI**
- [ ] Train **Regime Classifier** on 1 year of historical data (daily/weekly)
- [ ] Implement **Bayesian DQN** for spread optimization
- [ ] Build **Graph Neural Network** for cross-asset signals
- [ ] Integrate **on-chain data** via free subgraph APIs

### **Days 7-9: Risk & Integration**
- [ ] Program all **5 risk layers** with unit tests
- [ ] Implement **meta-learning** loop (MAML-style weight updates)
- [ ] Run **adversarial simulations**: 1000 Monte Carlo scenarios
- [ ] Generate **AI logs** and verify format compliance

### **Days 10-11: Testing & Documentation**
- [ ] **Paper trading** on WEEX testnet (if available) or dry-run
- [ ] Stress test: Simulate 90% drawdown scenario
- [ ] Optimize for **Sharpe > 2.0**, **Max DD < 10%** in backtests
- [ ] Write **Policy Description Document** with architecture diagrams

### **Days 12-14: Polish & Submit**
- [ ] Create **GitHub repo** with clean structure, MIT license
- [ ] Record **2-min demo video** (for Popularity Award)
- [ ] Submit **AI log** sample (50-100 trades) for verification
- [ ] Final API connection test, submit BUIDL

---

## **8. GitHub Repository Structure (Judges Will Review)**

```
weex-ai-hackathon/
├── README.md                    # Executive summary + architecture diagram
├── POLICY.md                    # Trading logic explained for non-experts
├── requirements.txt             # PyTorch, RAPIDS, PyMAB, etc.
├── src/
│   ├── agents/                  # Each agent as separate module
│   │   ├── orchestrator.py
│   │   ├── market_maker.py
│   │   └── momentum_agent.py
│   ├── risk/                    # 5-layer risk system
│   ├── features/                # GPU-accelerated feature engineering
│   └── utils/
│       ├── weex_ws.py          # WebSocket connector
│       └── ai_logger.py        # Structured logging for competition
├── config/
│   ├── competition.yaml        # Leverage, pairs, max position
│   └── hyperparams.yaml        # Model configs
├── notebooks/
│   └── eda.ipynb               # Feature analysis (show your work)
└── tests/
    └── test_risk_layers.py     # Demonstrate robustness
```

**Critical**: Include **Dockerfile** for reproducibility. Judges must run your code.

---

## **9. Mathematical Formulation (For Documentation)**

Show judges you understand the theory:

**Market Maker Spread Optimization:**
```latex
\max_{\delta^b, \delta^a} \mathbb{E}\left[\sum_{t=0}^{T} (p_t - m_t) \cdot q_t - \gamma \cdot \text{Inventory}_t^2\right]
```

**where:**
- $p_t$ = executed price, $m_t$ = mid-price
- $q_t$ = quantity (buy/sell)
- $\gamma$ = inventory aversion parameter (learned via meta-RL)

**Uncertainty-Aware Position Sizing:**
```latex
\text{Position Size} = \text{Kelly} \times (1 - \frac{\sigma_{\text{pred}}}{\sigma_{\text{max}}}) \times I_{\text{var} < \text{threshold}}
```

---

## **10. Winning Edge: What Judges Want to See**

Based on typical fintech hackathons (e.g., Jane Street, Two Sigma):

1. **Novelty**: Meta-learning + neuro-symbolic is **rare** in open competitions
2. **Rigor**: Bayesian uncertainty + adversarial testing shows maturity
3. **Interpretability**: Attention maps + SHAP values in AI logs
4. **Scalability**: GPU-accelerated, cloud-native architecture
5. **Ethics**: No wash trading, transparent logging, safety shutdowns
6. **Web3 Alignment**: Decentralized agent architecture mirrors blockchain ethos

**Popularity Award Hack**: Post **daily PnL updates** on Twitter/X with `#WEEXAIWars` and tag `@weex_ai`. Share **attention visualizations** showing how your AI "thinks."

---

## **11. Quickstart Commands**

```bash
# Setup (Day 1)
git clone https://github.com/your-repo/weex-ai-hackathon
cd weex-ai-hackathon
pip install -r requirements
docker build -t weex-ai-trader .

# Dry run (Day 10)
python -m src.main --mode paper --capital 1000 --leverage 10

# Generate AI log (Day 13)
python -m src.utils.ai_logger --output submission_log.json --verify
```

---

## **Final Warning: Common Failure Modes**

- **API rate limits**: Implement exponential backoff, circuit breaker pattern
- **Memory leaks**: Use `tracemalloc` in Python, monitor GPU memory
- **Slippage**: Never use market orders; limit orders only with 0.1% max slippage
- **Overfitting**: **No** in-sample optimization; use walk-forward validation only
- **Disqualification**: **Never** trade outside the 8 pairs; **always** submit valid AI logs

**Bottom line**: Build a **minimum viable agent** (Market Maker + Risk Layer) by Day 5, then iterate. A working simple system beats a broken complex one.

---

**Need help with specific implementation?** Ask for code snippets for any component (e.g., Bayesian DQN, GPU feature engineering, AI logger). Time is short—prioritize ruthlessly.
