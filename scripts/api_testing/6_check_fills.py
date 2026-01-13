import time
import hmac
import hashlib
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WEEX_API_KEY")
secret_key = os.getenv("WEEX_SECRET_KEY")
access_passphrase = os.getenv("WEEX_PASSPHRASE")

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

  url = "https://api-contract.weex.com/"  # Please replace with the actual API address
  if method == "GET":
    response = requests.get(url + request_path+query_string, headers=headers)
  return response

def fills():
    request_path = "/capi/v2/order/fills"
    query_string = "?symbol=cmt_btcusdt" # Removed orderId to check all recent fills as per likelihood of user not having ID
    response = send_request_get(api_key, secret_key, access_passphrase, "GET", request_path, query_string)
    print(response.status_code)
    print(response.text)

if __name__ == '__main__':
    fills()
