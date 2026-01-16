# 🧠 The Perp-Optimized AI Trading System (PAAT-E)

## Overview
**PAAT-E** (Perp-Optimized Adaptive AI Trading - Enhanced) is a trading system built specifically for the **WEEX AI Hackathon**. Unlike traditional bots that gamble on price direction, PAAT-E primarily exploits the unique mechanics of **Perpetual Futures**: **Funding Rates** and **Liquidation Cascades**.

It leverages **CoinGecko API** for market discovery and **WEEX API** for execution, orchestrated by a **Gaussian Mixture Model (GMM)** AI.

---

## 💎 The Edge: Why This Strategy Wins
Perpetual futures have a mechanism called **Funding Rate**:
- If most people are **LONG**, they pay shorts. (**Positive Funding**) -> We go **SHORT** to get paid.
- If most people are **SHORT**, they pay longs. (**Negative Funding**) -> We go **LONG** to get paid.

**We get paid to hold positions.** The price direction is secondary. This is "Market Neutral" thinking.

---

## 🧩 System Architecture

```mermaid
graph TD
    Market[Market Data] --> Scout(CoinGecko Scout)
    Market --> Data(WEEX Feeds)
    
    subgraph "AI Brain"
        Data --> Regime{Regime Classifier (GMM)}
        Regime -->|Calm| Agent1[Max Yield Mode]
        Regime -->|Volatile| Agent2[Defensive Mode]
    end
    
    subgraph "Strategy: Funding Arb"
        Agent1 --> Logic[Check Funding Rate]
        Logic -->|Funding > 0.01%| Short(Enter SHORT)
        Logic -->|Funding < -0.01%| Long(Enter LONG)
    end
    
    Short --> Risk{Risk Engine}
    Long --> Risk
    
    Risk -->|Approved| Exec(Execute on WEEX)
```

---

## 🤖 AI Components

### 1. The Scout: CoinGecko Integration
**Role**: Market Discovery.
**File**: `src/data/coingecko_loader.py`
Before we trade, we need to know *what* to trade. The Scout scans the top 200 coins on CoinGecko to find assets with **High Volatility** but sufficient volume.
- **Why?** Trend following and funding arb work best in moving markets, not dead ones.

### 2. The General: Regime Classifier (GMM)
**Role**: Context Awareness.
**File**: `src/ai/regime_classifier.py`
A **Gaussian Mixture Model** (Unsupervised Learning) analyzes recent price and volume data to classify the market into one of three "Regimes":
- **Regime 0: Calm** (Low Volatility). Safe to use higher leverage. Best for collecting funding.
- **Regime 1: Trend** (Directional). Good for momentum.
- **Regime 2: Volatile/Crash** (Extreme). **DANGER**. The system reduces leverage or halts new trades to prevent liquidation.

### 3. The Agent: Funding Rate Arbitrageur
**Role**: Signal Generation.
**File**: `src/ai/funding_agent.py`
This agent doesn't look at charts like a human. It looks at the **cost of money**.
- **Signal**: If Funding Rate > `0.0001` (0.01%), it implies the market is over-long. The agent signals **SHORT**.
- **Signal**: If Funding Rate < `-0.0001`, it signals **LONG**.

---

## 🛡️ Risk Management (The Shield)
**File**: `src/execution/risk_engine.py`
AI is probabilistic; Risk Management is deterministic. The Shield can override the AI.

| Rule | Calm Regime | Volatile Regime |
| :--- | :--- | :--- |
| **Max Leverage** | 10x | 2x (Survival Mode) |
| **Stop Loss** | 1% | 3% (Wider to avoid wicks) |
| **Position Size** | Normal | 50% Reduced |

---

## 🚀 Execution Flow (The Loop)
1. **Wake Up**: Bot starts (`src/main.py`).
2. **Scan**: `CoinGeckoLoader` finds the hot coin of the hour.
3. **Download**: `WeexClient` fetches candles and current Funding Rate.
4. **Think**: `RegimeClassifier` decides if it's safe.
5. **Decide**: `FundingAgent` checks if there's free money (funding yield).
6. **Validate**: `RiskEngine` approves the size and leverage.
7. **Act**: Order sent to WEEX.
8. **Record**: detailed log saved to `ai_trading_log.json`.
