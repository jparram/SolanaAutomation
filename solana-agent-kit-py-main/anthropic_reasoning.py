"""
Anthropic-powered reasoning engine for Solana trading signals
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
import time

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)

class AnthropicReasoningEngine:
    """
    Reasoning engine that uses Anthropic's Claude to analyze trading signals
    and make trading decisions based on market conditions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the reasoning engine with an Anthropic API key.
        
        Args:
            api_key: Anthropic API key. If None, will attempt to read from environment variable.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("No Anthropic API key provided. Reasoning engine will operate in simulation mode.")
            self.client = None
        else:
            try:
                if Anthropic:
                    self.client = Anthropic(api_key=self.api_key)
                    logger.info("Anthropic reasoning engine initialized successfully")
                else:
                    logger.warning("Anthropic package not installed. Reasoning engine will operate in simulation mode.")
                    self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
    
    def analyze_signals(self, 
                       ticker: str,
                       signals: Dict[str, Any], 
                       market_data: Dict[str, Any], 
                       historical_data: List[Dict[str, Any]],
                       token_info: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Analyzes trading signals and market data to determine if a trade should be executed.
        
        Args:
            ticker: The ticker symbol for the token
            signals: Dictionary of trading signals
            market_data: Current market data
            historical_data: Historical price and volume data
            token_info: Additional information about the token
            
        Returns:
            Tuple of (should_trade, confidence_score, reasoning)
        """
        if not self.client:
            # Simulation mode - make a simple decision based on signals
            return self._simulate_analysis(signals, market_data)
        
        # Format data for the prompt
        prompt = self._format_analysis_prompt(ticker, signals, market_data, historical_data, token_info)
        
        try:
            # Call Anthropic API
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",  # Use latest available model
                max_tokens=1000,
                system=self._get_system_prompt(),
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response to extract decision and reasoning
            response_text = message.content[0].text if hasattr(message, 'content') and message.content else ""
            return self._parse_analysis_response(response_text)
            
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            # Fall back to simulation mode if API call fails
            return self._simulate_analysis(signals, market_data)
    
    def _get_system_prompt(self) -> str:
        """Returns the system prompt for the reasoning engine."""
        return """
        You are an expert cryptocurrency trading analyst with deep knowledge of Solana tokens.
        Your task is to analyze trading signals and market data to make trading decisions.
        
        For each analysis request:
        1. Carefully review all provided signals, market data, and token information
        2. Consider both technical indicators and fundamental factors
        3. Assess the current market conditions and token-specific developments
        4. Provide a clear trading recommendation (BUY, SELL, or HOLD)
        5. Include a confidence score between 0.0 and 1.0 (where 1.0 is highest confidence)
        6. Explain your reasoning in a structured manner
        
        Your response must be in JSON format with these keys:
        {
            "decision": "BUY|SELL|HOLD",
            "confidence_score": float,
            "reasoning": "Your detailed analysis explaining the decision"
        }
        """
    
    def _format_analysis_prompt(self, 
                               ticker: str,
                               signals: Dict[str, Any], 
                               market_data: Dict[str, Any], 
                               historical_data: List[Dict[str, Any]],
                               token_info: Dict[str, Any]) -> str:
        """Formats the analysis prompt for Anthropic."""
        # Convert data structures to formatted strings for the prompt
        signals_str = json.dumps(signals, indent=2)
        market_data_str = json.dumps(market_data, indent=2)
        
        # Only include the last 5 entries of historical data to keep the prompt concise
        recent_history = historical_data[-5:] if historical_data else []
        history_str = json.dumps(recent_history, indent=2)
        token_info_str = json.dumps(token_info, indent=2)
        
        return f"""
        Please analyze the following trading data for {ticker} and provide a trading recommendation:
        
        ## Trading Signals
        {signals_str}
        
        ## Current Market Data
        {market_data_str}
        
        ## Recent Historical Data
        {history_str}
        
        ## Token Information
        {token_info_str}
        
        Based on this data, should I buy, sell, or hold this token? Provide your analysis as structured JSON with decision, confidence_score, and reasoning.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Tuple[bool, float, str]:
        """
        Parses the response from Anthropic to extract the trading decision.
        
        Returns:
            Tuple of (should_trade, confidence_score, reasoning)
        """
        try:
            # Extract JSON from the response
            # First, try to find JSON block in markdown format
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no markdown JSON block, try to find a JSON-like structure
                json_match = re.search(r'({.*})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # If still no match, use the whole response
                    json_str = response_text
            
            # Parse the JSON
            result = json.loads(json_str)
            
            # Extract decision, confidence score, and reasoning
            decision = result.get("decision", "HOLD").upper()
            confidence_score = float(result.get("confidence_score", 0.5))
            reasoning = result.get("reasoning", "No reasoning provided")
            
            # Convert decision to a boolean indicating whether to trade
            should_trade = decision == "BUY" or decision == "SELL"
            
            return should_trade, confidence_score, reasoning
            
        except Exception as e:
            logger.error(f"Error parsing Anthropic response: {str(e)}")
            return False, 0.5, f"Failed to parse analysis response: {str(e)}"
    
    def _simulate_analysis(self, signals: Dict[str, Any], market_data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Simulates an analysis when the Anthropic API is not available.
        
        Returns:
            Tuple of (should_trade, confidence_score, reasoning)
        """
        # Simple logic: if more positive signals than negative, recommend buying
        positive_signals = 0
        negative_signals = 0
        
        # Count positive and negative signals
        for signal_name, signal_value in signals.items():
            if isinstance(signal_value, bool):
                if signal_value:
                    positive_signals += 1
                else:
                    negative_signals += 1
            elif isinstance(signal_value, (int, float)):
                if signal_value > 0:
                    positive_signals += 1
                elif signal_value < 0:
                    negative_signals += 1
        
        # Determine if we should trade and with what confidence
        if positive_signals > negative_signals:
            confidence_score = min(0.5 + (positive_signals - negative_signals) * 0.1, 0.9)
            reasoning = f"Simulation mode: {positive_signals} positive signals vs {negative_signals} negative signals"
            return True, confidence_score, reasoning
        else:
            confidence_score = max(0.5 - (negative_signals - positive_signals) * 0.1, 0.1)
            reasoning = f"Simulation mode: {positive_signals} positive signals vs {negative_signals} negative signals"
            return False, confidence_score, reasoning
