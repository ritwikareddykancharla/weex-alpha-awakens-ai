import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WEEX_API_KEY")
secret_key = os.getenv("WEEX_SECRET_KEY")
access_passphrase = os.getenv("WEEX_PASSPHRASE")

def send_request_get( method, request_path, query_string):
  url = "https://api-contract.weex.com/"  # Please replace with the actual API address
  if method == "GET":
    response = requests.get(url + request_path+query_string)
  return response

def ticker():
    request_path = "/capi/v2/market/ticker"
    query_string = "?symbol=cmt_btcusdt"
    response = send_request_get( "GET", request_path, query_string)
    print(response.status_code)
    print(response.text)

if __name__ == '__main__':
    ticker()
