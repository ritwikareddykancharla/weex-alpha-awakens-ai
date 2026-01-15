import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.websocket_client import WeexWSClient

def on_account_update(data):
    """Callback when account data arrives"""
    # Data structure: see user provided JSON
    # It contains a list of collateral info
    try:
        # data is usually nested in msg->data->collateral in push, 
        # but our client passes data.get("data") which might be the inner dict or list
        print(f"💰 ACCOUNT UPDATE: {data}")
    except Exception as e:
        print(f"Error parse: {e}")

def main():
    print("Initializing Private WebSocket (Account)...")
    
    # Enable Private Mode (Auth)
    ws = WeexWSClient(use_private=True)
    ws.start()
    
    # Wait a sec for connection
    time.sleep(2)
    
    # Subscribe to Account Channel
    ws.subscribe_account(on_account_update)
    
    print("Listening for account updates (30s)...")
    print("NOTE: You might not see updates unless balance changes.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
