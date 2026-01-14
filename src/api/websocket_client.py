import json
import time
import threading
import websocket
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class WeexWSClient:
    """
    WebSocket Client for WEEX Exchange.
    Handles connection, heartbeats, and data streaming.
    """
    def __init__(self, public_url="wss://ws-contract.weex.com/v2/ws/public"):
        self.url = public_url
        self.ws = None
        self.thread = None
        self.is_running = False
        self.callbacks = {} # channel -> callback_function
        
    def start(self):
        """Starts the WebSocket in a background thread"""
        self.is_running = True
        self.ws = websocket.WebSocketApp(
            self.url,
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
        """
        Subscribes to a channel.
        example: ws.subscribe("kline.LAST_PRICE.cmt_btcusdt.MINUTE_1", my_func)
        """
        self.callbacks[channel] = callback
        
        if self.ws and self.ws.keep_running:
            payload = {
                "event": "subscribe",
                "channel": channel
            }
            self.ws.send(json.dumps(payload))
            logger.info(f"Subscribed to {channel}")
        else:
            logger.warning("WebSocket not connected. Subscription queued (logic pending).")

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
