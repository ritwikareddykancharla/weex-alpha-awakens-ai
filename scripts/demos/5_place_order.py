import time
import hmac
import hashlib
import base64
import requests
import json
import os
from dotenv import load_dotenv

# Load keys
load_dotenv()
api_key = os.getenv("WEEX_API_KEY")
secret_key = os.getenv("WEEX_SECRET_KEY")
access_passphrase = os.getenv("WEEX_PASSPHRASE")

# --- Authentication ---
def generate_signature(secret_key, timestamp, method, request_path, query_string, body):
  message = timestamp + method.upper() + request_path + query_string + str(body)
  signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
  return base64.b64encode(signature).decode()

def send_request_post(api_key, secret_key, access_passphrase, method, request_path, query_string, body):
  timestamp = str(int(time.time() * 1000))
  body_json = json.dumps(body)
  signature = generate_signature(secret_key, timestamp, method, request_path, query_string, body_json)
  headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": access_passphrase,
        "Content-Type": "application/json",
        "locale": "en-US"
  }
  url = "https://api-contract.weex.com"
  print(f"--- {method} {request_path} (Private API) ---")
  if method == "POST":
    response = requests.post(url + request_path, headers=headers, data=body_json)
  return response

# --- Main Logic ---
def placeOrder():
    request_path = "/capi/v2/order/placeOrder"
    
    # NOTE: Using 0.0001 BTC for safety, instead of 0.01
    # Price is dummy 100000.0, it will likely not fill if market is lower, which is safer.
    body = {
        "symbol": "cmt_btcusdt",
        "client_oid": f"demo_order_{int(time.time())}",
        "size": "0.0001", 
        "type": "1",    # 1: Open Long
        "order_type": "0", # 0: Limit Order
        "match_price": "0",
        "price": "100000.0" # Buying high @ Limit usually fills immediately if price is lower
    }
    
    query_string = ""
    try:
        response = send_request_post(api_key, secret_key, access_passphrase, "POST", request_path, query_string, body)
        print(f"Status: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if not api_key:
        print("Error: WEEX_API_KEY not found in .env")
    else:
        placeOrder()
