import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.websocket_client import WeexWSClient
from src.api.weex_client import WeexAPIClient

def on_account_update(data):
    """Callback when account data arrives"""
    print(f"💰 ACCOUNT UPDATE (WS): {data}")

def main():
    print("=== WEEX Account Data Test ===")
    
    # 1. Get Initial Balance (REST)
    print("1. Fetching Initial Balance via REST API...")
    try:
        api = WeexAPIClient()
        balance = api.get_account_balance()
        print(f"✅ Initial Balance: {balance}")
    except Exception as e:
        print(f"❌ Failed to fetch REST balance: {e}")
        print("Check your API Keys in .env")

    # 2. Start WebSocket (Real-time updates)
    print("\n2. Initializing Private WebSocket (Auth)...")
    ws = WeexWSClient(use_private=True)
    ws.start()
    
    time.sleep(2)
    ws.subscribe_account(on_account_update)
    
    print("Listening for account updates (30s)...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
