import google.generativeai as genai
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """
    Client for interacting with Google's Gemini Models.
    Used for 'Dialectical Debate' and 'Contextual Analysis'.
    """
    def __init__(self, model_name: str = "gemini-1.5-flash", system_instruction: str = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        
        # Configure model with System Instruction if provided
        if system_instruction:
            self.model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
        else:
            self.model = genai.GenerativeModel(model_name)
        
    def analyze_market_debate(self, bull_case: str, bear_case: str, technical_data: Dict[str, Any], position_context: str = "", history_context: str = "") -> Dict[str, Any]:
        """
        Synthesize a Bull vs Bear debate using Gemini's reasoning.
        """
        prompt = f"""
        CONTEXT (RECENT HISTORY):
        {history_context}
        
        CURRENT SITUATION:
        {position_context}
        
        TECHNICAL DATA: {json.dumps(technical_data)}
        
        BULL CASE: {bull_case}
        
        BEAR CASE: {bear_case}
        
        INSTRUCTIONS:
        1. Weigh the evidence from both sides.
        2. Consider the current market regime (Volatility, Trend).
        3. Output a final decision in JSON format.
        
        OUTPUT FORMAT:
        {{
            "decision": "BUY", "SELL", or "HOLD",
            "confidence": 0.0 to 1.0,
            "reasoning": "Brief explanation of the synthesis",
            "winner": "bull" or "bear"
        }}
        """
        
        response = self.model.generate_content(prompt)
        
        try:
            # Extract JSON from response
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except Exception as e:
            return {
                "decision": "HOLD",
                "confidence": 0.5,
                "reasoning": f"Failed to parse Gemini response: {str(e)}",
                "winner": "none"
            }
