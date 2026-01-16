# 🗺️ Strategy Roadmap: PAAT-E Evolution

This document tracks the current state of the **Perp-Optimized Adaptive AI Trading (PAAT-E)** system and outlines the roadmap for critical improvements to maximize competitiveness in the WEEX AI Wars.

## 🛡️ Current Core Strategy (Status: **Operational**)

**"PAAT-E" (Perp-Optimized Adaptive AI - Enhanced)**
A Market Neutral strategy designed to extract yield from funding rates rather than predicting price direction.

*   **Core Mechanic**: **Funding Rate Arbitrage**
    *   *Logic*: Long/Short based on funding polarity (Positive -> Short, Negative -> Long).
    *   *Edge*: Captures guaranteed yield from market imbalances.
*   **AI Engine**: **GMM Regime Classifier** (Unsupervised Learning)
    *   *Logic*: Classifies market as "Calm", "Trending", or "Volatile".
    *   *Edge*: dynamically adjusts leverage and risk parameters (e.g., 10x in Calm, 2x in Volatile).
*   **Discovery**: **CoinGecko Scout**
    *   *Logic*: Scans top 200 coins for volatility and volume.
    *   *Edge*: Ensures capital is deployed in the most active markets.

---

## 🚀 Improvement Roadmap (The "Winning" Features)

The following upgrades are planned to increase ROI and safety during the competition.

### 1. Liquidation Fading (Priority: **HIGH**)
*   **Concept**: Profiting from "forced selling" cascades. When price crashes -5% not because of news, but because of liqudations, price often snaps back instantly.
*   **Implementation**:
    *   Monitor 1-minute aggregations for massive volume spikes + price drops.
    *   Enter contrarian position (Long the dip) for short duration (30s - 5m).
*   **Status**: ⬜ *Pending Implementation*

### 2. Human-in-the-Loop "Kill Switch" (Priority: **HIGH**)
*   **Concept**: Emergency safety valve for Black Swan events.
*   **Implementation**:
    *   Simple Telegram Bot or CLI command (`/stop`) to:
        1.  Cancel all open orders.
        2.  Close all open positions (Market).
        3.  Terminate the bot process.
*   **Status**: ⬜ *Pending Implementation*

### 3. Dynamic Funding Thresholds (Priority: **MEDIUM**)
*   **Concept**: Replace fixed thresholds (e.g., `0.01%`) with statistical significance.
*   **Implementation**:
    *   Calculate Z-Score of current Funding Rate relative to 24h moving average.
    *   Trigger trades only when Z-Score > 2 (statistically significant anomaly).
*   **Status**: ⬜ *Pending Implementation*

### 4. Sentiment Analysis Shield (Priority: **LOW**)
*   **Concept**: "News moves price." Detect bad news before the candle prints.
*   **Implementation**:
    *   Scrape X (Twitter) for "WEEX", "Hack", "Delisting", "SEC".
    *   Halt buy orders if Sentiment Score drops below threshold.
*   **Status**: ⬜ *Pending Implementation*

---

## 📅 Action Plan

1.  [x] **Core System**: Basic Funding Arb + GMM (Complete).
2.  [x] **Connectivity**: API Whitelist & Verification (Complete).
3.  [ ] **Upgrade 1**: Implement Liquidation Fading module.
4.  [ ] **Upgrade 2**: Deploy Kill Switch.
5.  [ ] **Optimization**: Backtest Dynamic Thresholds.
