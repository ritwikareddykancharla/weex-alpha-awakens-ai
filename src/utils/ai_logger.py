import json
import os
from datetime import datetime
from typing import Dict, Any

class AIJournal:
    """
    Logs every 'thought' the AI has.
    Satisfies the Hackathon requirement for 'AI Logging'.
    """
    def __init__(self, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "ai_brain_journal.jsonl")
        
    def log_decision(self, 
                     market_state: Dict[str, Any], 
                     bull_case: str, 
                     bear_case: str, 
                     ai_response: Dict[str, Any]):
        """
        Record the dialectical debate and final synthesis.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "context": {
                "market_state": market_state,
                "bull_case": bull_case,
                "bear_case": bear_case
            },
            "gemini_verdict": ai_response,
            "metadata": {
                "model": "gemini-1.5-pro",
                "strategy": "Dialectical Debate"
            }
        }
        
        # Append to JSONL (JSON Lines) file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
    def get_recent_history(self, limit: int = 5) -> str:
        """
        Retrieve recent decisions to build 'Context' for the AI.
        THIS IS HOW WE GIVE GEMINI MEMORY.
        """
        history = []
        if not os.path.exists(self.log_file):
            return "No previous trade history."
            
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    data = json.loads(line)
                    verdict = data.get('gemini_verdict', {})
                    history.append(f"- {data['timestamp']}: Decided {verdict.get('decision')} (Conf: {verdict.get('confidence')}). Reason: {verdict.get('reasoning')}")
        except Exception:
            return "Error reading history."
            
        return "\n".join(history)
