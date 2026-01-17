import sys
import os
import json
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.api.weex_client import WeexAPIClient
from src.utils.logger import setup_logger

logger = setup_logger("fetch_account_info")

def main():
    try:
        client = WeexAPIClient()
        
        # User-Agent for WAF/Cloudflare
        client.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
        print("\n🔍 connectivity Test (Public Proxy)...")
        try:
            response = client._request("GET", "/capi/v2/market/time")
            print(f"✅ Connection Successful! Server Time: {response}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            return

        print("\n🔍 Fetching Account Information (Probing Endpoints)...")
        
        endpoints = [
            "/capi/v2/account/getAccounts",
            "/capi/v2/account/assets",
            "/capi/v2/account/info",
            "/capi/v2/user/info"
        ]

        for ep in endpoints:
            print(f"\n--- Trying {ep} ---")
            try:
                data = client._request("GET", ep)
                print(json.dumps(data, indent=2))
                print(f"✅ SUCCESS: {ep}")
            except Exception as e:
                print(f"❌ FAILED {ep}: {e}")
            
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")

if __name__ == "__main__":
    main()
