import time
import hmac
import hashlib
import base64
import json
from typing import Dict, List, Optional, Any
import requests
from requests.exceptions import RequestException

from src.utils.logger import setup_logger
from src.utils.validators import validate_response
from config.settings import config

logger = setup_logger(__name__)

class WeexAPIClient:
    """WEEX API Client with authentication and error handling"""
    
    def __init__(self):
        self.base_url = config.BASE_URL
        self.api_key = config.API_KEY
        self.secret_key = config.SECRET_KEY
        self.passphrase = config.PASSPHRASE
        self.session = requests.Session()
        
    def _generate_signature(self, timestamp: str, method: str, 
                          request_path: str, body: str = "") -> str:
        """Generate HMAC SHA256 signature"""
        message = timestamp + method.upper() + request_path + body
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_headers(self, method: str, request_path: str, 
                    body: str = "") -> Dict[str, str]:
        """Generate authentication headers"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(
            timestamp, method, request_path, body
        )
        
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "locale": "en-US"
        }
    
    def _request(self, method: str, endpoint: str, 
                params: Dict = None, data: Dict = None) -> Dict:
        """Make authenticated request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(method, endpoint, 
                                   json.dumps(data) if data else "")
        
        try:
            if method == "GET":
                response = self.session.get(
                    url, headers=headers, params=params, timeout=10
                )
            elif method == "POST":
                response = self.session.post(
                    url, headers=headers, json=data, timeout=10
                )
            elif method == "DELETE":
                response = self.session.delete(
                    url, headers=headers, json=data, timeout=10
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    # Account Methods
    def get_account_balance(self) -> List[Dict]:
        """Get account balance"""
        return self._request("GET", "/capi/v2/account/assets")
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """Get current positions"""
        endpoint = "/capi/v2/account/positions"
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", endpoint, params=params)
    
    def set_leverage(self, symbol: str, leverage: int, 
                    margin_mode: int = 1) -> Dict:
        """Set leverage for a symbol"""
        data = {
            "symbol": symbol,
            "marginMode": margin_mode,
            "longLeverage": str(leverage),
            "shortLeverage": str(leverage)
        }
        return self._request("POST", "/capi/v2/account/leverage", data=data)
    
    # Market Data Methods
    def get_ticker(self, symbol: str) -> Dict:
        """Get ticker data for symbol"""
        return self._request("GET", f"/capi/v2/market/ticker?symbol={symbol}")
    
    def get_klines(self, symbol: str, interval: str = "5min", 
                  limit: int = 100) -> List[List]:
        """Get candlestick data"""
        params = {
            "symbol": symbol,
            "granularity": interval,  # Changed from interval to granularity
            "limit": min(limit, 100)  # Max 100 per request
        }
        return self._request("GET", "/capi/v2/market/historyCandles", params=params)
    
    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict:
        """Get order book depth"""
        return self._request(
            "GET", f"/capi/v2/market/depth?symbol={symbol}&depth={depth}"
        )
        
    def get_funding_rate_history(self, symbol: str, page_size: int = 10) -> List[Dict]:
        """Get historical funding rates (Critical for Strategy)"""
        params = {
            "symbol": symbol,
            "pageSize": page_size,
            "pageIndex": 1
        }
        return self._request("GET", "/capi/v2/market/fundingRate", params=params)

    def get_open_interest(self, symbol: str) -> Dict:
        """Get Open Interest (Critical for Regime Detection)"""
        return self._request("GET", f"/capi/v2/market/openInterest?symbol={symbol}")
        
    # Order Methods
    def place_order(self, symbol: str, side: str, order_type: str,
                   quantity: float, price: float = None,
                   client_order_id: str = None) -> Dict:
        """Place a new order"""
        data = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "volume": str(quantity),
            "positionSide": "BOTH"
        }
        
        if price:
            data["price"] = str(price)
        if client_order_id:
            data["clientOrderId"] = client_order_id
        
        return self._request("POST", "/capi/v2/order", data=data)
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an order"""
        data = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/capi/v2/order", data=data)
    
    def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """Get order status"""
        return self._request(
            "GET", f"/capi/v2/order?symbol={symbol}&orderId={order_id}"
        )
    
    # Test connection
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.session.get(
                f"{self.base_url}/capi/v2/market/time",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
