"""
Risk analysis module for Solana Trading Desktop
Using Solana Tracker API to analyze token risk and provide risk scores
"""
import os
import logging
import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """
    Risk analyzer for Solana tokens using the Solana Tracker API
    to evaluate token risk factors and generate risk scores.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the risk analyzer with a Solana Tracker API key.
        
        Args:
            api_key: Solana Tracker API key. If None, will attempt to read from environment variable.
        """
        self.api_key = api_key or os.getenv("SOLANA_TRACKER_API_KEY")
        self.base_url = "https://data.solanatracker.io"
        
        if not self.api_key:
            logger.warning("No Solana Tracker API key provided. Risk analysis will be simulated.")
    
    def get_token_risk(self, token_address: str) -> Dict[str, Any]:
        """
        Get risk analysis for a specific token.
        
        Args:
            token_address: The Solana token address to analyze
            
        Returns:
            Dictionary containing risk analysis data
        """
        if not self.api_key:
            return self._simulate_risk_analysis(token_address)
            
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/tokens/{token_address}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Extract risk information if available
                risk_data = data.get("risk", {})
                return self._process_risk_data(risk_data, token_address)
            else:
                logger.error(f"Error getting token risk: {response.status_code}, {response.text}")
                return self._simulate_risk_analysis(token_address)
                
        except Exception as e:
            logger.error(f"Error analyzing token risk: {str(e)}")
            return self._simulate_risk_analysis(token_address)
    
    def _process_risk_data(self, risk_data: Dict[str, Any], token_address: str) -> Dict[str, Any]:
        """Process the risk data from the API response."""
        if not risk_data:
            return self._simulate_risk_analysis(token_address)
            
        # Extract risk score and factors
        risk_score = risk_data.get("score", 5)
        risk_factors = risk_data.get("risks", [])
        is_rugged = risk_data.get("rugged", False)
        
        # Categorize risk factors
        warning_factors = []
        danger_factors = []
        liquidity_factors = []
        
        for factor in risk_factors:
            level = factor.get("level", "").lower()
            if level == "warning":
                warning_factors.append(factor)
            elif level == "danger":
                danger_factors.append(factor)
            elif "liquidity" in factor.get("name", "").lower():
                liquidity_factors.append(factor)
                
        return {
            "token_address": token_address,
            "risk_score": risk_score,
            "is_rugged": is_rugged,
            "warning_factors": warning_factors,
            "danger_factors": danger_factors,
            "liquidity_factors": liquidity_factors,
            "total_risk_factors": len(risk_factors),
            "risk_category": self._get_risk_category(risk_score),
            "safe_to_trade": risk_score < 7 and not is_rugged
        }
    
    def _get_risk_category(self, risk_score: int) -> str:
        """Categorize risk based on score."""
        if risk_score <= 3:
            return "Low Risk"
        elif risk_score <= 6:
            return "Moderate Risk"
        elif risk_score <= 8:
            return "High Risk"
        else:
            return "Extreme Risk"
            
    def get_token_market_data(self, token_address: str) -> Dict[str, Any]:
        """
        Get market data for a specific token.
        
        Args:
            token_address: The Solana token address
            
        Returns:
            Dictionary containing market data
        """
        if not self.api_key:
            return self._simulate_market_data(token_address)
            
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/price?token={token_address}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_market_data(data, token_address)
            else:
                logger.error(f"Error getting market data: {response.status_code}, {response.text}")
                return self._simulate_market_data(token_address)
                
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return self._simulate_market_data(token_address)
    
    def _process_market_data(self, market_data: Dict[str, Any], token_address: str) -> Dict[str, Any]:
        """Process the market data from the API response."""
        if not market_data:
            return self._simulate_market_data(token_address)
            
        try:
            # Extract the relevant market data
            price_usd = market_data.get("price", {}).get("usd", 0)
            price_change = market_data.get("priceChange", {})
            market_cap = market_data.get("marketCap", {}).get("usd", 0)
            liquidity = market_data.get("liquidity", {}).get("usd", 0)
            
            return {
                "token_address": token_address,
                "price_usd": price_usd,
                "market_cap_usd": market_cap,
                "liquidity_usd": liquidity,
                "price_change_1h": price_change.get("1h", 0),
                "price_change_24h": price_change.get("24h", 0),
                "price_change_7d": price_change.get("7d", 0)
            }
        except Exception as e:
            logger.error(f"Error processing market data: {str(e)}")
            return self._simulate_market_data(token_address)
    
    def get_token_stats(self, token_address: str) -> Dict[str, Any]:
        """
        Get trading statistics for a specific token.
        
        Args:
            token_address: The Solana token address
            
        Returns:
            Dictionary containing token statistics
        """
        if not self.api_key:
            return self._simulate_token_stats(token_address)
            
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/stats/{token_address}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting token stats: {response.status_code}, {response.text}")
                return self._simulate_token_stats(token_address)
                
        except Exception as e:
            logger.error(f"Error getting token stats: {str(e)}")
            return self._simulate_token_stats(token_address)
    
    def calculate_combined_risk_score(self, 
                                     risk_data: Dict[str, Any], 
                                     market_data: Dict[str, Any], 
                                     stats_data: Dict[str, Any]) -> Tuple[int, str]:
        """
        Calculate a comprehensive risk score using all available data.
        
        Args:
            risk_data: Risk analysis data
            market_data: Market data
            stats_data: Token statistics data
            
        Returns:
            Tuple of (risk_score, explanation)
        """
        base_risk = risk_data.get("risk_score", 5)
        
        # Market-based risk factors
        market_risk_factors = []
        
        # Check for concerning market trends
        price_change_24h = market_data.get("price_change_24h", 0)
        liquidity = market_data.get("liquidity_usd", 0)
        
        if price_change_24h < -30:
            market_risk_factors.append("Significant price drop in last 24h")
        
        if liquidity < 1000:
            market_risk_factors.append("Very low liquidity")
        elif liquidity < 5000:
            market_risk_factors.append("Low liquidity")
        
        # Adjust risk score based on market factors
        adjusted_risk = base_risk
        
        for _ in market_risk_factors:
            adjusted_risk = min(10, adjusted_risk + 0.5)
        
        # Generate explanation
        explanation = f"Base risk score: {base_risk}/10"
        if risk_data.get("is_rugged", False):
            explanation += " (WARNING: Token appears to be rugged)"
        
        if market_risk_factors:
            explanation += "\nMarket risk factors: " + ", ".join(market_risk_factors)
        
        danger_factors = risk_data.get("danger_factors", [])
        if danger_factors:
            factors = [f["name"] for f in danger_factors]
            explanation += "\nDanger factors: " + ", ".join(factors)
        
        category = self._get_risk_category(adjusted_risk)
        explanation += f"\nRisk category: {category}"
        
        return round(adjusted_risk), explanation
    
    def get_comprehensive_token_analysis(self, token_address: str) -> Dict[str, Any]:
        """
        Get comprehensive token analysis including risk, market data, and statistics.
        
        Args:
            token_address: The Solana token address to analyze
            
        Returns:
            Dictionary with comprehensive analysis
        """
        risk_data = self.get_token_risk(token_address)
        market_data = self.get_token_market_data(token_address)
        stats_data = self.get_token_stats(token_address)
        
        combined_score, explanation = self.calculate_combined_risk_score(risk_data, market_data, stats_data)
        
        return {
            "token_address": token_address,
            "risk_analysis": risk_data,
            "market_data": market_data,
            "token_stats": stats_data,
            "combined_risk_score": combined_score,
            "risk_explanation": explanation,
            "timestamp": int(time.time())
        }
    
    def _simulate_risk_analysis(self, token_address: str) -> Dict[str, Any]:
        """Simulate risk analysis when API is not available."""
        # Generate simulated risk based on the token address hash
        hash_value = sum(ord(c) for c in token_address)
        simulated_risk = (hash_value % 10) + 1
        
        return {
            "token_address": token_address,
            "risk_score": simulated_risk,
            "is_rugged": simulated_risk > 8,
            "warning_factors": [
                {"name": "Simulated warning factor", "level": "warning", "score": 100}
            ] if simulated_risk > 3 else [],
            "danger_factors": [
                {"name": "Simulated danger factor", "level": "danger", "score": 5000}
            ] if simulated_risk > 7 else [],
            "liquidity_factors": [],
            "total_risk_factors": 1 if simulated_risk > 3 else 0,
            "risk_category": self._get_risk_category(simulated_risk),
            "safe_to_trade": simulated_risk < 7
        }
    
    def _simulate_market_data(self, token_address: str) -> Dict[str, Any]:
        """Simulate market data when API is not available."""
        # Generate simulated price data based on the token address hash
        hash_value = sum(ord(c) for c in token_address)
        
        simulated_price = round(hash_value % 1000 / 100, 4)
        simulated_change = round((hash_value % 40) - 20, 2)
        
        return {
            "token_address": token_address,
            "price_usd": simulated_price,
            "market_cap_usd": simulated_price * 1000000,
            "liquidity_usd": simulated_price * 50000,
            "price_change_1h": simulated_change / 2,
            "price_change_24h": simulated_change,
            "price_change_7d": simulated_change * 1.5
        }
    
    def _simulate_token_stats(self, token_address: str) -> Dict[str, Any]:
        """Simulate token statistics when API is not available."""
        # Generate simulated stats based on the token address hash
        hash_value = sum(ord(c) for c in token_address)
        
        return {
            "token_address": token_address,
            "buys_24h": hash_value % 50,
            "sells_24h": hash_value % 30,
            "volume_24h": hash_value % 10000,
            "unique_buyers_24h": hash_value % 20,
            "unique_sellers_24h": hash_value % 15,
            "simulated": True
        }
