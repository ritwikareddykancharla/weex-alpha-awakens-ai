import time
import hmac
import hashlib
import base64
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WEEX_API_KEY")
secret_key = os.getenv("WEEX_SECRET_KEY")
access_passphrase = os.getenv("WEEX_PASSPHRASE")

def generate_signature(secret_key, timestamp, method, request_path, query_string, body):
  message = timestamp + method.upper() + request_path + query_string + str(body)
  signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
  return base64.b64encode(signature).decode()

def send_request_post(api_key, secret_key, access_passphrase, method, request_path, query_string, body):
  timestamp = str(int(time.time() * 1000))
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
  url = "https://api-contract.weex.com/"  # Please replace with the actual API address
  if method == "POST":
    response = requests.post(url + request_path, headers=headers, data=body)
  return response

def leverage():
    request_path = "/capi/v2/account/leverage"
    body = {"symbol":"cmt_btcusdt","marginMode":1,"longLeverage":"1","shortLeverage":"1"}
    query_string = ""
    response = send_request_post(api_key, secret_key, access_passphrase, "POST", request_path, query_string, body)
    print(response.status_code)
    print(response.text)

if __name__ == '__main__':
    leverage()
