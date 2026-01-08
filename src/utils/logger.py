import logging
import json
from datetime import datetime
from typing import Dict, Any
import os

from config.settings import config

class AILogger:
    """Generates AI logs in WEEX required format"""
    
    def __init__(self, log_path: str = None):
        self.log_path = log_path or config.AI_LOG_PATH
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if not exists
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_path),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('ai_trading')
    
    def log_signal(self, signal_data: Dict[str, Any]):
        """Log trading signal in required format"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SIGNAL",
            "data": {
                "symbol": signal_data.get("symbol"),
                "signal": signal_data.get("signal"),
                "confidence": signal_data.get("confidence"),
                "indicators": signal_data.get("indicators", {}),
                "features": signal_data.get("features", [])
            }
        }
        
        self._write_log(log_entry)
        self.logger.info(f"Signal: {signal_data}")
    
    def log_order(self, order_data: Dict[str, Any]):
        """Log order placement"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "ORDER",
            "data": {
                "order_id": order_data.get("orderId"),
                "symbol": order_data.get("symbol"),
                "side": order_data.get("side"),
                "type": order_data.get("type"),
                "quantity": order_data.get("volume"),
                "price": order_data.get("price"),
                "status": order_data.get("status"),
                "client_order_id": order_data.get("clientOrderId")
            }
        }
        
        self._write_log(log_entry)
        self.logger.info(f"Order: {order_data}")
    
    def log_position(self, position_data: Dict[str, Any]):
        """Log position update"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "POSITION",
            "data": {
                "symbol": position_data.get("symbol"),
                "position_amt": position_data.get("positionAmt"),
                "entry_price": position_data.get("entryPrice"),
                "unrealized_pnl": position_data.get("unrealizedPnl"),
                "leverage": position_data.get("leverage")
            }
        }
        
        self._write_log(log_entry)
    
    def log_risk(self, risk_data: Dict[str, Any]):
        """Log risk metrics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "RISK",
            "data": risk_data
        }
        
        self._write_log(log_entry)
        self.logger.info(f"Risk Update: {risk_data}")
    
    def log_error(self, error_data: Dict[str, Any]):
        """Log error"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "ERROR",
            "data": error_data
        }
        
        self._write_log(log_entry)
        self.logger.error(f"Error: {error_data}")
    
    def _write_log(self, log_entry: Dict):
        """Write log entry to file"""
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to write log: {e}")
    
    def get_log_summary(self) -> Dict:
        """Generate log summary for competition submission"""
        try:
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
            
            signals = 0
            orders = 0
            errors = 0
            
            for line in lines:
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "SIGNAL":
                        signals += 1
                    elif entry.get("type") == "ORDER":
                        orders += 1
                    elif entry.get("type") == "ERROR":
                        errors += 1
                except:
                    continue
            
            return {
                "total_entries": len(lines),
                "signals": signals,
                "orders": orders,
                "errors": errors,
                "log_file": self.log_path,
                "last_updated": datetime.now().isoformat()
            }
            
        except FileNotFoundError:
            return {"error": "Log file not found"}

def setup_logger(name: str) -> logging.Logger:
    """Setup logger for modules"""
    return logging.getLogger(name)

# Global logger instance
ai_logger = AILogger()
