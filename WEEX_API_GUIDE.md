# WEEX API Strategy Guide for Neuro-Symbolic Engine

This guide maps the WEEX Futures API endpoints to the specific components of your **Neuro-Symbolic Adaptive Market Engine**.

## 🧠 Strategy-to-API Mapping

### 1. Market Maker Agent (Execution & Liquidity)
To capture spread and manage inventory, this agent needs real-time depth and fast execution.

| Signal Component | API Endpoint | Purpose |
| :--- | :--- | :--- |
| **Microstructure** | `GET /capi/v2/market/depth` | Order book imbalance, liquidity holes. |
| **Inventory** | `GET /capi/v2/account/positions` | Current size, unrealized PnL. (Derived from `getAccounts`) |
| **Execution** | `POST /capi/v2/order/placeOrder` | Placing Limit orders (Maker). |
| **Cancellation** | `POST /capi/v2/order/cancel` | Rapidly pulling quotes when toxic flow is detected. |

### 2. Momentum Agent (Directional Alpha)
For the Temporal Fusion Transformer (TFT) and Gradient Boosting models.

| Signal Component | API Endpoint | Purpose |
| :--- | :--- | :--- |
| **Trend History** | `GET /capi/v2/market/historyCandles` | OHLCV data for feature engineering (RSI, ATR). |
| **Price Action** | `GET /capi/v2/market/ticker` | 24h change, high/low, volume velocity. |
| **Funding Pressure** | `GET /capi/v2/market/currentFundRate` | Perpetual curve term structure. |

### 3. Risk Management Layer (The Shield)
The 5-layer defense system relies on account state and global metrics.

| Signal Component | API Endpoint | Purpose |
| :--- | :--- | :--- |
| **Capital Check** | `GET /capi/v2/account/getAccounts` | **Account Balance**, Margin Ratio, Frozen assets. |
| **Leverage Cap** | `POST /capi/v2/account/setLeverage` | Enforcing the 20x max limit dynamically. |
| **Liquidation Calc** | `WS channel: account` | Instant push alerts for margin calls. |

---

## 📚 API Reference Details

### 🟢 Public Data (No Auth Required)

#### 1. Get K-Line Data (Candles)
Used for training the AI model (`train_local.py`).
*   **Endpoint:** `GET /capi/v2/market/historyCandles`
*   **Params:** `symbol` (e.g., cmt_btcusdt), `granularity` (1m, 5m, 1h), `limit` (max 100).

#### 2. Get Order Book (Depth)
Used by the Market Maker for VPIN/OFI features.
*   **Endpoint:** `GET /capi/v2/market/depth`
*   **Params:** `symbol`, `depth` (e.g., 20).

#### 3. Get Funding Rate
Used for regime classification (High positive funding = Bullish euphoria).
*   **Endpoint:** `GET /capi/v2/market/currentFundRate`

---

### 🔒 Private Trading (Requires Auth)

#### 4. Get Account Info (Balance)
Your "Capital Allocator" uses this for Kelly Criterion sizing.
*   **Endpoint:** `GET /capi/v2/account/getAccounts`
*   **Call Code:** `client.get_account_balance()`

#### 5. Place Order
The final action of the execution agents.
*   **Endpoint:** `POST /capi/v2/order/placeOrder`
*   **Critical Params:**
    *   `type`: 1 (Open Long), 2 (Open Short), 3 (Close Long), 4 (Close Short)
    *   `match_price`: 0 (Limit), 1 (Market)
    *   `order_type`: 0 (Normal), 1 (Post-Only - **Critical for Market Making**)

---

## 🚀 Implementation Status

| API Function | Python Implementation | Status |
| :--- | :--- | :--- |
| **Auth** | `src.api.weex_client.WeexAPIClient` | ✅ Ready |
| **Market Data** | `client.get_klines()`, `get_depth()` | ✅ Ready |
| **Trading** | `client.place_order()` | ✅ Ready |
| **Account** | `client.get_account_balance()` | ✅ Ready |
| **WebSocket** | `src.api.websocket_client.WeexWSClient` | ✅ **Recently Upgraded** (Supports Account Channel) |

### 💡 Recommendation
Your strategy references "Microstructure Features" like **Order Flow Imbalance**. This requires **Order Book Snapshots via WebSocket**.
*   **Action:** Ensure the main bot subscribes to `depth` channel (not just K-lines) to calculate these features in real-time.
