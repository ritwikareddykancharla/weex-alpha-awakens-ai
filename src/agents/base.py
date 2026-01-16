from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import time
from src.api.weex_client import WeexAPIClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentDecision:
    def __init__(self, agent_name: str, signal: str, confidence: float, reasoning: str, data: Dict = None):
        self.agent_name = agent_name
        self.signal = signal # 'LONG', 'SHORT', 'NEUTRAL', 'BULLISH', 'BEARISH'
        self.confidence = confidence
        self.reasoning = reasoning
        self.data = data or {}
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "agent": self.agent_name,
            "signal": self.signal,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
            "data": self.data
        }

class BaseAgent(ABC):
    """
    Base Agent Class - Python Version of Fenyr's BaseAgent
    """
    def __init__(self, name: str, weex_client: WeexAPIClient):
        self.name = name
        self.weex = weex_client
        self.logger = setup_logger(f"Agent-{name}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Define the agent's persona and rules"""
        pass

    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> AgentDecision:
        """Main analysis logic"""
        pass

    def run_inference(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Mock LLM Inference (Replace with actual OpenAI/DeepSeek call)
        This mimics Fenyr's callGPT function.
        """
        # In a real "Fenyr-like" bot, you would import openai here
        # return openai.ChatCompletion.create(...)
        pass

    def log_decision(self, decision: AgentDecision):
        """Uploads decision to AI Log (Compliance)"""
        self.logger.info(f"[{self.name}] Signal: {decision.signal} ({decision.confidence*100:.1f}%)")
        self.logger.info(f"Reasoning: {decision.reasoning}")
        
        # Save to local JSON similar to Fenyr's uploadAILog
        log_entry = decision.to_dict()
        with open("ai_trading_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
