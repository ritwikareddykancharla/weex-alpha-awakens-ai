from .base_agent import BaseAgent
from src.ai.regime_classifier import RegimeClassifier
from src.ai.alpha_engine import AlphaEngine
import pandas as pd
from typing import Dict, Any

class MarketAnalyst(BaseAgent):
    """
    The 'Brain' & 'Eyes' of the system.
    Combines Regime Classification (GMM) and Alpha Prediction (ML).
    """
    def __init__(self, model_path_ml="models/trend_classifier.pkl", model_path_gmm="models/regime_gmm.pkl"):
        super().__init__("MarketAnalyst")
        
        # Sub-components
        self.eyes = RegimeClassifier(model_path=model_path_gmm)
        self.brain = AlphaEngine(model_path=model_path_ml)
        
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        1. Detect Regime (Risk Context)
        2. Predict Direction (Alpha)
        """
        df = market_data.get('klines_df')
        if df is None or df.empty:
            return {"signal": "NEUTRAL", "confidence": 0, "reason": "No Data"}

        # 1. Detect Regime
        regime = self.eyes.predict(df)
        regime_label = ["CALM", "TRENDING", "VOLATILE"][regime]
        
        # 2. Predict Signal
        # AlphaEngine expects a dict for market_data, we pass the raw tick info
        tick_info = {
            'fundingRate': market_data.get('fundingRate', 0),
            'markPrice': market_data.get('markPrice', 0)
        }
        
        alpha_result = self.brain.analyze(tick_info, regime, historical_data=df)
        
        return {
            "signal": alpha_result['action'],
            "confidence": alpha_result['confidence'],
            "regime": regime_label,
            "raw_regime": regime,
            "reason": f"[{regime_label}] {alpha_result['reason']}"
        }
