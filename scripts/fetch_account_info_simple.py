import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure we can import from src
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Explicitly load .env from project root
load_dotenv(os.path.join(project_root, '.env'))

from src.api.weex_client import WeexAPIClient

def main():
    print(f"Loading keys from environment...")
    if not os.getenv("WEEX_API_KEY"):
        print("❌ Error: WEEX_API_KEY not found in .env")
        return

    try:
        # Initialize client (It naturally uses the fixed logic now)
        client = WeexAPIClient()
        
        # Add User-Agent just in case
        client.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        print("\n🔍 Fetching Account Information (Whitelisted IP Mode)...")
        
        # The main endpoint for account assets/UID
        # /capi/v2/account/getAccounts usually returns standard account info
        try:
            print(f"Requesting: {client.base_url}/capi/v2/account/getAccounts")
            data = client._request("GET", "/capi/v2/account/getAccounts")
            print("\n✅ ACCOUNT DATA:")
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"❌ Failed to get account info: {e}")

        # Try assets endpoint as backup
        try:
            print(f"\nRequesting: {client.base_url}/capi/v2/account/assets")
            data = client._request("GET", "/capi/v2/account/assets")
            print("\n✅ ASSETS DATA:")
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"❌ Failed to get assets: {e}")
            
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
