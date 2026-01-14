import time
import hmac
import hashlib
import base64
import requests
import json
import os
from dotenv import load_dotenv

# Load keys from .env
load_dotenv()

API_KEY = os.getenv("WEEX_API_KEY")
SECRET_KEY = os.getenv("WEEX_SECRET_KEY")
PASSPHRASE = os.getenv("WEEX_PASSPHRASE")
BASE_URL = "https://api-contract.weex.com"

# --- Authentication Helpers ---
def generate_signature(timestamp, method, request_path, query_string, body):
    message = timestamp + method.upper() + request_path + query_string + str(body)
    signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def send_request(method, endpoint, params=None, body=None):
    request_path = endpoint
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()]) if params else ""
    body_str = json.dumps(body) if body else ""
    timestamp = str(int(time.time() * 1000))
    
    signature = generate_signature(timestamp, method, request_path, query_string, body_str)
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US"
    }
    
    url = f"{BASE_URL}{request_path}{query_string}"
    
    print(f"\n--- {method} {request_path} ---")
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=body_str)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...") # Truncate long responses
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return {}

# --- Step 1: Check Account Balance ---
def test_assets():
    print("\n[Step 1] Checking Assets...")
    res = send_request("GET", "/capi/v2/account/assets")
    return res

# --- Step 2: Get Ticker ---
def test_ticker(symbol="cmt_btcusdt"):
    print(f"\n[Step 2] Getting Ticker for {symbol}...")
    res = send_request("GET", "/capi/v2/market/ticker", params={"symbol": symbol})
    if 'last' in res:
        return float(res['last'])
    return None

# --- Step 3: Set Leverage ---
def test_leverage(symbol="cmt_btcusdt", leverage=5):
    print(f"\n[Step 3] Setting Leverage to {leverage}x...")
    body = {
        "symbol": symbol,
        "marginMode": 1, # Cross Margin
        "longLeverage": str(leverage),
        "shortLeverage": str(leverage)
    }
    send_request("POST", "/capi/v2/account/leverage", body=body)

# --- Step 4: Place Order (Test Trade) ---
def test_place_order(symbol="cmt_btcusdt", price=None):
    print("\n[Step 4] Placing Test Order...")
    
    # Calculate approx 10 USDT size
    # If price is 100k, 0.0001 BTC = 10 USDT
    # WEEX min size for BTC is usually 0.0001
    
    qty = "0.0001"
    trade_price = str(int(price * 0.9)) if price else "0" # Limit Buy 10% below market to be safe, or Market
    
    # User Guide says: "Execute a trade" -> imples FILL.
    # But safe test is Limit. Let's do a Limit Order far away first to test system.
    # IF you want to burn 10 USDT for the test, change type to "1" (Market).
    
    print(f"Placing LIMIT BUY for {qty} {symbol} at {trade_price}")
    
    body = {
        "symbol": symbol,
        "client_oid": f"test_{int(time.time())}",
        "size": qty,
        "type": "1", # 1=Open Long
        "order_type": "0", # 0=Limit
        "match_price": "0",
        "price": trade_price
    }
    
    res = send_request("POST", "/capi/v2/order/placeOrder", body=body)
    return res.get("order_id") if isinstance(res, dict) else None

# --- Step 5: Check Fills/Orders ---
def test_fills(symbol="cmt_btcusdt", order_id=None):
    print("\n[Step 5] Checking Order Details...")
    params = {"symbol": symbol}
    if order_id:
        params['orderId'] = order_id
        
    # Check open orders first
    print("Checking Open Orders...")
    send_request("GET", "/capi/v2/order/openOrders", params=params)
    
    # Check fills (if executed)
    print("Checking Fills...")
    send_request("GET", "/capi/v2/order/fills", params=params)

if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: API Keys not found in .env")
        exit(1)
        
    test_assets()
    price = test_ticker()
    test_leverage()
    
    if price:
        # WARNING: This places a LIVE ORDER.
        # Currently verifying connection/auth with a LIMIT order below price.
        order_id = test_place_order(price=price)
        if order_id:
            time.sleep(1) # Wait for propagation
            test_fills(order_id=order_id)
