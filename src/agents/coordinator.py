from .base_agent import BaseAgent
from .market_analyst import MarketAnalyst
from .risk_guardian import RiskGuardian
from .reasoning_agent import ReasoningAgent # <--- NEW
from typing import Dict, Any

class Coordinator(BaseAgent):
    """
    The 'Boss'.
    Orchestrates the consensus between Analyst, Reasoning, and Risk agents.
    """
    def __init__(self):
        super().__init__("Coordinator")
        self.analyst = MarketAnalyst()
        self.risk = RiskGuardian()
        self.brain = ReasoningAgent() # <--- NEW
        
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full Agent Loop:
        Data -> Analyst -> (Signal) -> Risk -> (Veto?) -> Decision
        """
        # 1. Ask Analyst (Hard-Coded / DQN)
        self.logger.info("📡 Requesting Market Analysis...")
        analysis = self.analyst.analyze(market_data)
        
        # 2. Ask Gemini (LLM Reasoning)
        self.logger.info("🧠 Requesting Gemini Reasoning...")
        ai_synthesis = self.brain.analyze(market_data)
        
        signal = analysis.get('signal')
        confidence = analysis.get('confidence', 0)
        regime = analysis.get('regime')
        
        # 3. Ask Risk Manager
        market_data_for_risk = market_data.copy()
        market_data_for_risk['proposed_action'] = signal
        market_data_for_risk['regime'] = regime
        
        risk_check = self.risk.analyze(market_data_for_risk)
        
        # 4. Final Consensus (LLM Weighting)
        final_decision = "NEUTRAL"
        
        # If AI and Analyst agree OR Confidence is high
        ai_decision = ai_synthesis.get('decision', 'HOLD')
        ai_confidence = ai_synthesis.get('confidence', 0)
        
        if risk_check['approved']:
            # Weighted synthesis: 60% Analyst, 40% AI
            if signal == ai_decision:
                final_decision = signal
            elif ai_confidence > 0.8:
                final_decision = ai_decision
            else:
                final_decision = signal # Default to safety of analyst
                
            suggested_size = risk_check.get('suggested_size', 0.0)
            stop_loss_dist = risk_check.get('stop_loss_dist', 0.0)
            
            final_reason = f"Combined Analysis: {analysis.get('reason')} | AI Synthesis: {ai_synthesis.get('reasoning')}"
        else:
            final_decision = "NEUTRAL"
            final_reason = f"Risk Veto: {risk_check['reason']}"
            self.logger.warning(f"🚫 Action {signal} VETOED by Risk Guardian")
            
        result = {
            "action": final_decision,
            "confidence": (confidence + ai_confidence) / 2,
            "regime": regime,
            "reason": final_reason,
            "size": suggested_size if final_decision != "NEUTRAL" else 0,
            "stop_loss_dist": stop_loss_dist 
        }
        
        self.logger.info(f"⚖️ Final Consensus: {result['action']} | Size: {result['size']} | {result['reason']}")
        return result
