from .base_agent import BaseAgent
from ..api.gemini_client import GeminiClient
from ..utils.ai_logger import AIJournal 
from ..api.weex_client import WeexAPIClient # <--- NEW
from typing import Dict, Any

class ReasoningAgent(BaseAgent):
    """
    LLM-powered Reasoning Agent.
    Implements 'Dialectical Debate' logic inspired by FENYR.
    """
    def __init__(self, model_name: str = "gemini-3.0-flash"):
        super().__init__("ReasoningAgent")
        self.journal = AIJournal()
        self.weex = WeexAPIClient()
        
        system_prompt = """
        You are the CHIEF STRATEGIST for an AI Hedge Fund (Alpha Awakens).
        Your goal is to MAXIMIZE PROFIT over a 2-week period.
        You use a Dialectical Approach: Weighing Bull vs Bear arguments.
        You rely on technical data but use YOUR reasoning to filter false signals.
        """
        
        try:
            self.client = GeminiClient(model_name=model_name, system_instruction=system_prompt)
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.client = None

    def analyze(self, market_data: Dict[str, Any], account_state: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.client:
            return {"decision": "HOLD", "confidence": 0, "reason": "Gemini not configured"}

        # 1. Retrieve Context
        history_context = self.journal.get_recent_history(limit=5)
        
        # 2. Generate cases
        bull_case = self._generate_bull_case(market_data)
        bear_case = self._generate_bear_case(market_data)
        
        # 3. Position Context
        position_context = ""
        if account_state and account_state.get('has_position'):
            position_context = f"""
            CURRENT POSITION STATUS:
            Side: {account_state['side']}
            Size: {account_state['size']}
            Unrealized PnL: {account_state['pnl']}
            Leverage: {account_state['leverage']}
            """

        # 4. Gemini Decision
        self.logger.info("🧠 Gemini is weighing Bull vs Bear arguments + Memory...")
        synthesis = self.client.analyze_market_debate(
            bull_case, bear_case, market_data, position_context, history_context
        )
        
        # 5. Log to Local Journal
        self.journal.log_decision(market_data, bull_case, bear_case, synthesis)
        
        # 6. Upload to WEEX (HACKATHON REQUIREMENT)
        self.logger.info("📡 Uploading AI Log to WEEX...")
        self.weex.upload_ai_log(
            stage="Strategy Generation",
            model="gemini-1.5-pro",
            input_data={
                "market_data": market_data,
                "bull_case": bull_case, 
                "bear_case": bear_case
            },
            output_data=synthesis,
            explanation=synthesis.get('reasoning', 'AI Decision based on technicals and sentiment.')
        )
        
        return synthesis

    def _generate_bull_case(self, data: Dict[str, Any]) -> str:
        # Heuristic/Template Bull Arguments
        return f"Momentum is positive. RSI is not yet overbought. Funding is neutral. Price is above EMA 100."

    def _generate_bear_case(self, data: Dict[str, Any]) -> str:
        # Heuristic/Template Bear Arguments
        return f"Market volume is thinning. Standard deviation is rising (Bollinger Expansion). We are approaching resistance."
