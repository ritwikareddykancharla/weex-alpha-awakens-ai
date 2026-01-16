from .base_agent import BaseAgent
from .market_analyst import MarketAnalyst
from .risk_guardian import RiskGuardian
from typing import Dict, Any

class Coordinator(BaseAgent):
    """
    The 'Boss'.
    Orchestrates the consensus between Analyst and Risk agents.
    """
    def __init__(self):
        super().__init__("Coordinator")
        self.analyst = MarketAnalyst()
        self.risk = RiskGuardian()
        
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full Agent Loop:
        Data -> Analyst -> (Signal) -> Risk -> (Veto?) -> Decision
        """
        # 1. Ask Analyst
        self.logger.info("📡 Requesting Market Analysis...")
        analysis = self.analyst.analyze(market_data)
        
        signal = analysis.get('signal')
        confidence = analysis.get('confidence', 0)
        regime = analysis.get('regime')
        
        self.log_decision(analysis)
        
        # 2. Ask Risk Manager
        # Pass the proposed action to Risk Manager
        market_data_for_risk = market_data.copy()
        market_data_for_risk['proposed_action'] = signal
        market_data_for_risk['regime'] = regime
        
        risk_check = self.risk.analyze(market_data_for_risk)
        
        # 3. Final Consensus
        final_decision = "NEUTRAL"
        final_reason = analysis.get('reason')
        
        if risk_check['approved']:
            final_decision = signal
            if final_decision != "NEUTRAL":
                final_reason = f"Approved Trade: {final_reason}"
        else:
            final_decision = "NEUTRAL"
            final_reason = f"Risk Veto: {risk_check['reason']}"
            self.logger.warning(f"🚫 Action {signal} VETOED by Risk Guardian")
            
        result = {
            "action": final_decision,
            "confidence": confidence,
            "regime": regime,
            "reason": final_reason
        }
        
        self.logger.info(f"⚖️ Final Consensus: {result['action']} | {result['reason']}")
        return result
