import time
import hmac
import hashlib
import base64
import requests
import json
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime
from collections import deque

# --- CONFIGURATION (FILL THESE) ---
API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"
PASSPHRASE = "YOUR_PASSPHRASE"
BASE_URL = "https://api-contract.weex.com"

# --- STRATEGY PARAMETERS ---
SYMBOL = "cmt_dogeusdt"  # High Volatility Coin
LEVERAGE = 5             # Keep it safe (Max is 20, we use 5)
TIMEFRAME = "15m"        # 15 Minute candles
CONFIDENCE_THRESHOLD = 0.75  # AI must be 75% sure to trade
RISK_PER_TRADE = 0.02    # Risk 2% of equity per trade

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AlphaSniper")

# ==========================================
# 1. WEEX API HANDLER
# ==========================================
class WeexClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "locale": "en-US"})

    def _sign(self, method, path, query="", body=""):
        timestamp = str(int(time.time() * 1000))
        message = timestamp + method.upper() + path + query + str(body)
        signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        return base64.b64encode(signature).decode(), timestamp

    def request(self, method, endpoint, params=None, body=None):
        query = "?" + "&".join([f"{k}={v}" for k, v in params.items()]) if params else ""
        body_str = json.dumps(body) if body else ""
        signature, timestamp = self._sign(method, endpoint, query, body_str)
        
        headers = {
            "ACCESS-KEY": API_KEY, "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp, "ACCESS-PASSPHRASE": PASSPHRASE
        }
        try:
            url = f"{BASE_URL}{endpoint}{query}"
            resp = self.session.request(method, url, headers=headers, data=body_str)
            return resp.json()
        except Exception as e:
            logger.error(f"API Error: {e}")
            return None

    def get_kline(self, symbol, limit=100):
        # Fetches historical candles for AI training
        # Note: Adjust endpoint if specific 'kline' endpoint differs in contest docs
        return self.request("GET", "/capi/v2/market/historyCandles", 
                          params={"symbol": symbol, "limit": min(limit, 100), "granularity": TIMEFRAME})

    def get_balance(self):
        data = self.request("GET", "/capi/v2/account/assets")
        if data and isinstance(data, list):
            for asset in data:
                if asset['coinName'] == 'USDT':
                    return float(asset['available'])
        return 0.0

    def place_order(self, side, size, price=None):
        # side: 1=OpenLong, 2=CloseShort, 3=OpenShort, 4=CloseLong
        payload = {
            "symbol": SYMBOL,
            "size": str(size),
            "type": str(side),
            "order_type": "0" if price else "1", # 0=Limit, 1=Market
            "price": str(price) if price else "0",
            "match_price": "1" if not price else "0"
        }
        return self.request("POST", "/capi/v2/order/placeOrder", body=payload)

# ==========================================
# 2. THE AI MODEL (LSTM)
# ==========================================
class LSTMConfig:
    input_size = 5  # Features: Close, RSI, MACD, Volatility, Volume
    hidden_size = 64
    num_layers = 2
    output_size = 1 # Probability of UP

class CryptoLSTM(nn.Module):
    def __init__(self, config):
        super(CryptoLSTM, self).__init__()
        self.lstm = nn.LSTM(config.input_size, config.hidden_size, 
                            config.num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(config.hidden_size, config.output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch, seq_len, features)
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :]) # Take last time step
        return self.sigmoid(out)

# ==========================================
# 3. FEATURE ENGINEERING & LOGIC
# ==========================================
class AlphaBrain:
    def __init__(self):
        self.model = CryptoLSTM(LSTMConfig())
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()
        self.scaler_mean = 0
        self.scaler_std = 1

    def prepare_data(self, candles):
        # Convert API kline data to DataFrame
        # Format: [time, open, high, low, close, vol...]
        df = pd.DataFrame(candles, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'a', 'b'])
        df['close'] = df['close'].astype(float)
        df['vol'] = df['vol'].astype(float)
        
        # --- Technical Indicators (Manual Calc to avoid lib dependency issues) ---
        # 1. RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 2. MACD
        exp12 = df['close'].ewm(span=12, adjust=False).mean()
        exp26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp12 - exp26
        
        # 3. Volatility (Bollinger Band Width)
        df['sma'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['volatility'] = (2 * df['std']) / df['sma']

        # Drop NaNs
        df.dropna(inplace=True)
        
        # Normalize
        features = df[['close', 'rsi', 'macd', 'volatility', 'vol']].values
        self.scaler_mean = features.mean(axis=0)
        self.scaler_std = features.std(axis=0)
        normalized_features = (features - self.scaler_mean) / (self.scaler_std + 1e-8)
        
        return torch.FloatTensor(normalized_features), df

    def train_live(self, candles):
        # Online Learning: Update model on latest data
        data, df = self.prepare_data(candles)
        if len(data) < 20: return 0.0
        
        # Create sequences
        X, y = [], []
        for i in range(10, len(data)-1):
            X.append(data[i-10:i]) # Sequence of 10 candles
            # Label: 1 if next Close > current Close, else 0
            label = 1 if data[i+1][0] > data[i][0] else 0
            y.append(label)
            
        X_tensor = torch.stack(X)
        y_tensor = torch.FloatTensor(y).unsqueeze(1)
        
        # Train Step
        self.model.train()
        self.optimizer.zero_grad()
        preds = self.model(X_tensor)
        loss = self.criterion(preds, y_tensor)
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

    def predict(self, candles):
        self.model.eval()
        data, df = self.prepare_data(candles)
        if len(data) < 11: return 0.5, {}
        
        # Get last sequence
        last_seq = data[-10:].unsqueeze(0) # Shape (1, 10, 5)
        
        with torch.no_grad():
            prob = self.model(last_seq).item()
            
        latest_features = {
            "rsi": df['rsi'].iloc[-1],
            "macd": df['macd'].iloc[-1],
            "volatility": df['volatility'].iloc[-1]
        }
        return prob, latest_features

# ==========================================
# 4. EXECUTION ENGINE
# ==========================================
def generate_ai_log(action, symbol, prob, features):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "symbol": symbol,
        "action": action,
        "ai_confidence": round(prob, 4),
        "model": "LSTM_Hybrid_v1",
        "features": {k: round(v, 4) for k, v in features.items()},
        "rationale": f"LSTM probability {prob:.2f} > threshold. RSI confirms trend."
    }
    with open("ai_trading_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    logger.info(f"AI Log Saved: {action}")

def run_bot():
    client = WeexClient()
    brain = AlphaBrain()
    
    logger.info("Initializing AlphaSniper...")
    
    # Check Balance
    balance = client.get_balance()
    logger.info(f"Account Balance: {balance} USDT")

    while True:
        try:
            # 1. Fetch Data
            candles = client.get_kline(SYMBOL)
            if not candles:
                time.sleep(5)
                continue

            # 2. Train Model (Online Learning)
            loss = brain.train_live(candles)
            logger.info(f"Model Updated. Loss: {loss:.4f}")

            # 3. Predict
            prob, features = brain.predict(candles)
            logger.info(f"Prediction (UP): {prob:.2f} | RSI: {features.get('rsi', 0):.1f}")

            # 4. Trading Logic
            # BUY SIGNAL
            if prob > CONFIDENCE_THRESHOLD and features['rsi'] < 70:
                # Calculate Size
                entry_price = float(candles[-1][4]) # Close price
                position_size_usdt = balance * RISK_PER_TRADE * LEVERAGE
                qty_contracts = position_size_usdt / entry_price
                
                logger.info(f"SIGNAL: BUY! Size: {qty_contracts:.4f}")
                
                # Execute
                # resp = client.place_order(side=1, size=qty_contracts) # Uncomment to Trade
                
                # Log
                generate_ai_log("OPEN_LONG", SYMBOL, prob, features)

            # SELL SIGNAL
            elif prob < (1 - CONFIDENCE_THRESHOLD) and features['rsi'] > 30:
                logger.info("SIGNAL: SELL / SHORT!")
                # Execute logic for shorting...
                generate_ai_log("OPEN_SHORT", SYMBOL, prob, features)

            time.sleep(60) # Wait for next candle/minute

        except Exception as e:
            logger.error(f"Loop Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
