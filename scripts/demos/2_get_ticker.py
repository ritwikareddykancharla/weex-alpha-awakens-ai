import requests

# --- Helpers ---
def send_request_get(method, request_path, query_string):
  url = "https://api-contract.weex.com"
  print(f"--- {method} {request_path} (Public API) ---")
  if method == "GET":
    response = requests.get(url + request_path + query_string)
  return response

# --- Main Logic ---
def ticker():
    request_path = "/capi/v2/market/ticker"
    query_string = "?symbol=cmt_btcusdt"
    try:
        response = send_request_get("GET", request_path, query_string)
        print(f"Status: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    ticker()
