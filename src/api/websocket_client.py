import json
import time
import threading
import websocket
import hmac
import hashlib
import base64
from typing import Dict
from src.utils.logger import setup_logger
from config.settings import config

logger = setup_logger(__name__)

class WeexWSClient:
    """
    WebSocket Client for WEEX Exchange.
    Handles connection, heartbeats, and data streaming.
    Supports both Public and Private channels.
    """
    def __init__(self, use_private=False):
        self.public_url = "wss://ws-contract.weex.com/v2/ws/public"
        self.private_url = "wss://ws-contract.weex.com/v2/ws/private"
        self.use_private = use_private
        self.url = self.private_url if use_private else self.public_url
        
        self.ws = None
        self.thread = None
        self.is_running = False
        self.callbacks = {} # channel -> callback_function
        
        # Load Auth creds
        self.api_key = config.API_KEY
        self.secret_key = config.SECRET_KEY
        self.passphrase = config.PASSPHRASE

    def _generate_signature(self, timestamp: str, request_path: str) -> str:
        """Generate HMAC SHA256 signature for WS login"""
        # For WS, message is timestamp + request_path (No Method)
        message = timestamp + request_path
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')

    def start(self):
        """Starts the WebSocket in a background thread"""
        self.is_running = True
        
        headers = {"User-Agent": "Mozilla/5.0"}
        
        if self.use_private:
            # Generate Private Auth Headers
            timestamp = str(int(time.time() * 1000))
            request_path = "/v2/ws/private"
            signature = self._generate_signature(timestamp, request_path)
            
            headers.update({
                "ACCESS-KEY": self.api_key,
                "ACCESS-SIGN": signature,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": self.passphrase
            })
            logger.info("Connecting to Private WebSocket with Auth...")

        self.ws = websocket.WebSocketApp(
            self.url,
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"WebSocket Client started on {self.url}")

    def subscribe(self, channel, callback):
        """Generic subscription"""
        self.callbacks[channel] = callback
        if self.ws and self.ws.keep_running:
            payload = {"event": "subscribe", "channel": channel}
            self.ws.send(json.dumps(payload))
            logger.info(f"Subscribed to {channel}")

    def subscribe_account(self, callback):
        """Subscribe to Account Channel (requires Private connection)"""
        if not self.use_private:
            logger.error("Cannot subscribe to Account channel on Public connection! Use WeexWSClient(use_private=True)")
            return
        self.subscribe("account", callback)

    def _on_open(self, ws):
        logger.info("WebSocket Connected")
        # Re-subscribe if needed (logic can be expanded)

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            
            # 1. Handle Ping (Server Heartbeat)
            if "event" in data and data["event"] == "ping":
                # Respond with Pong
                pong = {"event": "pong", "time": data["time"]}
                ws.send(json.dumps(pong))
                # logger.debug("Pong sent")
                return

            # 2. Handle Push Data
            if "event" in data and data["event"] == "push":
                channel = data.get("channel")
                if channel in self.callbacks:
                    # Pass the 'data' field (contains kline/price info) to callback
                    self.callbacks[channel](data.get("data"))
            
            # 3. Handle Subscription Confirmations
            elif "event" in data and data["event"] == "subscribed":
                logger.info(f"Subscription Confirmed: {data.get('channel')}")

        except Exception as e:
            logger.error(f"WS Message Error: {e}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket Closed")
        self.is_running = False
