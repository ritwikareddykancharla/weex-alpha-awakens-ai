import time
import hmac
import hashlib
import base64
import requests
import os
from dotenv import load_dotenv

# Load keys
load_dotenv()
api_key = os.getenv("WEEX_API_KEY")
secret_key = os.getenv("WEEX_SECRET_KEY")
access_passphrase = os.getenv("WEEX_PASSPHRASE")

# --- Authentication ---
def generate_signature_get(secret_key, timestamp, method, request_path, query_string):
  message = timestamp + method.upper() + request_path + query_string
  signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
  return base64.b64encode(signature).decode()

def send_request_get(api_key, secret_key, access_passphrase, method, request_path, query_string):
  timestamp = str(int(time.time() * 1000))
  signature = generate_signature_get(secret_key, timestamp, method, request_path, query_string)
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
  if method == "GET":
    response = requests.get(url + request_path + query_string, headers=headers)
  return response

# --- Main Logic ---
def fills():
    request_path = "/capi/v2/order/fills"
    # Note: You need a real orderId here usually, or fetch recent fills without ID if supported (not guaranteed by all params)
    # The demo code has "?symbol=cmt_btcusdt&orderId=YOUR_ORDER_ID"
    # We will try just symbol to see if it returns list
    query_string = "?symbol=cmt_btcusdt" 
    
    try:
        response = send_request_get(api_key, secret_key, access_passphrase, "GET", request_path, query_string)
        print(f"Status: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if not api_key:
        print("Error: WEEX_API_KEY not found in .env")
    else:
        fills()
