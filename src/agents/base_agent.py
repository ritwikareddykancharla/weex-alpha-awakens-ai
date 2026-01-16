from abc import ABC, abstractmethod
from typing import Dict, Any
from src.utils.logger import setup_logger

class BaseAgent(ABC):
    """
    Abstract Base Class for all AI Agents in the Neuro-Symbolic System.
    """
    def __init__(self, name: str):
        self.name = name
        self.logger = setup_logger(f"Agent-{name}")
        self.logger.info(f"🦾 Agent Initialized: {name}")

    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process market data and return a decision or analysis.
        
        Args:
            market_data: Dictionary containing klines, orderbook, funding, etc.
            
        Returns:
            Dictionary with keys like 'signal', 'confidence', 'reason', 'metadata'
        """
        pass

    def log_decision(self, decision: Dict):
        """Standardized logging for agent decisions"""
        self.logger.info(f"[{self.name}] Decision: {decision}")
