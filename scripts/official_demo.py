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

api_key = os.getenv("WEEX_API_KEY")
secret_key = os.getenv("WEEX_SECRET_KEY")
access_passphrase = os.getenv("WEEX_PASSPHRASE")

def generate_signature(secret_key, timestamp, method, request_path, query_string, body):
  message = timestamp + method.upper() + request_path + query_string + str(body)
  signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
  # print(base64.b64encode(signature).decode())
  return base64.b64encode(signature).decode()


def generate_signature_get(secret_key, timestamp, method, request_path, query_string):
  message = timestamp + method.upper() + request_path + query_string
  signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
  # print(base64.b64encode(signature).decode())
  return base64.b64encode(signature).decode()


def send_request_post(api_key, secret_key, access_passphrase, method, request_path, query_string, body):
  timestamp = str(int(time.time() * 1000))
  # print(timestamp)
  body = json.dumps(body)
  signature = generate_signature(secret_key, timestamp, method, request_path, query_string, body)

  headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": access_passphrase,
        "Content-Type": "application/json",
        "locale": "en-US"
  }

  url = "https://api-contract.weex.com" 
  if method == "GET":
    response = requests.get(url + request_path, headers=headers)
  elif method == "POST":
    response = requests.post(url + request_path, headers=headers, data=body)
  return response

def send_request_get(api_key, secret_key, access_passphrase, method, request_path, query_string):
  timestamp = str(int(time.time() * 1000))
  # print(timestamp)
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
  if method == "GET":
    response = requests.get(url + request_path+query_string, headers=headers)
  return response

def get():
    # Example of calling a GET request
    # Changed to 'ticker' because 'singlePosition' requires an open position to show data usually
    request_path = "/capi/v2/market/ticker"
    query_string = '?symbol=cmt_btcusdt'
    print(f"GET {request_path}")
    response = send_request_get(api_key, secret_key, access_passphrase, "GET", request_path, query_string)
    print(response.status_code)
    print(response.text)

def post():
    # Example of calling a POST request
    request_path = "/capi/v2/order/placeOrder"
    body = {
	"symbol": "cmt_btcusdt",
	"client_oid": f"demo_{int(time.time())}", # Use unique ID
	"size": "0.0001", # Changed from 0.01 (Wait too big) to 0.0001 (Safe test size)
	"type": "1",
	"order_type": "1", # Market Order to ensure fill for test, or 0 for limit
	"match_price": "1",
	"price": "0"} # Market order ignores price
    query_string = ""
    print(f"POST {request_path}")
    response = send_request_post(api_key, secret_key, access_passphrase, "POST", request_path, query_string, body)
    print(response.status_code)
    print(response.text)

if __name__ == '__main__':
    if not api_key:
        print("Error: WEEX_API_KEY not set in .env")
        exit(1)
    get()
    # post() # Commented out to prevent accidental spending. Uncomment to test order.
