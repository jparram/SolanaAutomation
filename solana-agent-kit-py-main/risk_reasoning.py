"""
Integrated risk assessment and reasoning module for Solana trading
Combines Solana Tracker API risk data with Anthropic's Claude for intelligent analysis
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple

from risk_analyzer import RiskAnalyzer
from anthropic_reasoning import AnthropicReasoningEngine

logger = logging.getLogger(__name__)

class RiskReasoningEngine:
    """
    Combines token risk analysis with AI reasoning to produce
    intelligent trading signals and risk assessments.
    """
    
    def __init__(self, tracker_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        """
        Initialize the risk reasoning engine.
        
        Args:
            tracker_api_key: Solana Tracker API key
            anthropic_api_key: Anthropic API key
        """
        self.risk_analyzer = RiskAnalyzer(api_key=tracker_api_key)
        self.reasoning_engine = AnthropicReasoningEngine(api_key=anthropic_api_key)
        logger.info("Risk reasoning engine initialized")
    
    def analyze_token_with_reasoning(self, token_address: str, token_symbol: str) -> Dict[str, Any]:
        """
        Perform comprehensive token analysis with AI reasoning.
        
        Args:
            token_address: The Solana token address to analyze
            token_symbol: The token symbol (e.g., SOL, USDC)
            
        Returns:
            Dictionary with analysis results and AI reasoning
        """
        # Get token risk and market data
        token_analysis = self.risk_analyzer.get_comprehensive_token_analysis(token_address)
        
        # Prepare data for AI reasoning
        signals = {
            "risk_score": token_analysis.get("combined_risk_score", 5),
            "safe_to_trade": token_analysis.get("risk_analysis", {}).get("safe_to_trade", True),
            "price_change_24h": token_analysis.get("market_data", {}).get("price_change_24h", 0),
            "price_change_7d": token_analysis.get("market_data", {}).get("price_change_7d", 0)
        }
        
        market_data = token_analysis.get("market_data", {})
        
        # Create token info dictionary
        token_info = {
            "symbol": token_symbol,
            "address": token_address,
            "risk_factors": self._extract_risk_factors(token_analysis),
            "risk_explanation": token_analysis.get("risk_explanation", "")
        }
        
        # Get AI reasoning about the token
        should_trade, confidence, reasoning = self.reasoning_engine.analyze_signals(
            ticker=token_symbol,
            signals=signals,
            market_data=market_data,
            historical_data=[],  # We could add historical data here if available
            token_info=token_info
        )
        
        # Combine everything into a comprehensive analysis
        return {
            "token_symbol": token_symbol,
            "token_address": token_address,
            "risk_score": token_analysis.get("combined_risk_score", 5),
            "market_data": market_data,
            "signals": signals,
            "should_trade": should_trade,
            "confidence_score": confidence,
            "ai_reasoning": reasoning,
            "raw_risk_data": token_analysis.get("risk_analysis", {}),
            "timestamp": token_analysis.get("timestamp", 0)
        }
    
    def _extract_risk_factors(self, token_analysis: Dict[str, Any]) -> List[str]:
        """Extract risk factors from token analysis."""
        risk_factors = []
        
        # Get risk factors from analysis
        risk_analysis = token_analysis.get("risk_analysis", {})
        
        # Extract warning factors
        for factor in risk_analysis.get("warning_factors", []):
            name = factor.get("name", "")
            if name:
                risk_factors.append(f"Warning: {name}")
        
        # Extract danger factors
        for factor in risk_analysis.get("danger_factors", []):
            name = factor.get("name", "")
            if name:
                risk_factors.append(f"DANGER: {name}")
        
        # Extract liquidity factors
        for factor in risk_analysis.get("liquidity_factors", []):
            name = factor.get("name", "")
            if name:
                risk_factors.append(f"Liquidity: {name}")
        
        return risk_factors
    
    def get_trading_recommendation(self, token_symbol: str, token_address: str, amount: float) -> Dict[str, Any]:
        """
        Get a trading recommendation for a specific token.
        
        Args:
            token_symbol: The token symbol
            token_address: The Solana token address
            amount: The amount being considered for the trade
            
        Returns:
            Dictionary with trading recommendation
        """
        # Get comprehensive analysis
        analysis = self.analyze_token_with_reasoning(token_address, token_symbol)
        
        # Determine recommendation based on risk score and AI reasoning
        risk_score = analysis.get("risk_score", 5)
        should_trade = analysis.get("should_trade", False)
        confidence = analysis.get("confidence_score", 0.5)
        
        if risk_score >= 8:
            recommendation = "DO NOT TRADE - EXTREME RISK"
            explanation = f"This token has an extremely high risk score of {risk_score}/10."
            adjusted_amount = 0.0
        elif risk_score >= 6:
            recommendation = "CAUTION - HIGH RISK" 
            if should_trade and confidence > 0.8:
                explanation = "Despite high risk, AI analysis suggests a potential opportunity with high confidence."
                adjusted_amount = amount * 0.25  # Reduce position size due to risk
            else:
                explanation = f"This token has a high risk score of {risk_score}/10. Trading not recommended."
                adjusted_amount = 0.0
        else:
            if should_trade:
                if confidence > 0.8:
                    recommendation = "RECOMMENDED TRADE"
                    explanation = "AI analysis indicates a favorable opportunity with high confidence."
                    adjusted_amount = amount
                else:
                    recommendation = "POTENTIAL OPPORTUNITY"
                    explanation = "AI analysis suggests a potential opportunity but with moderate confidence."
                    adjusted_amount = amount * 0.5
            else:
                recommendation = "NOT RECOMMENDED"
                explanation = "AI analysis does not support trading this token at this time."
                adjusted_amount = 0.0
        
        return {
            "token_symbol": token_symbol,
            "recommendation": recommendation,
            "explanation": explanation,
            "risk_score": risk_score, 
            "confidence_score": confidence,
            "recommended_amount": adjusted_amount,
            "original_amount": amount,
            "ai_reasoning": analysis.get("ai_reasoning", "No reasoning provided"),
            "risk_factors": analysis.get("raw_risk_data", {}).get("warning_factors", []) + 
                           analysis.get("raw_risk_data", {}).get("danger_factors", [])
        }
