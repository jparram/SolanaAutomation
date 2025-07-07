"""
Natural Language Processing Controller for Solana Trading Desktop
"""
import os
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)

class NLPController:
    """
    Natural language interface to control the Solana Trading Desktop.
    Uses Anthropic Claude to parse user commands and translate them into
    application actions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the NLP controller.
        
        Args:
            api_key: Anthropic API key. If None, will attempt to read from environment variable.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.commands = {
            "buy": self._handle_buy,
            "sell": self._handle_sell,
            "check_price": self._handle_check_price,
            "check_balance": self._handle_check_balance,
            "show_portfolio": self._handle_show_portfolio,
            "analyze_token": self._handle_analyze_token,
            "set_trade_limit": self._handle_set_trade_limit,
            "help": self._handle_help,
        }
        
        if not self.api_key:
            logger.warning("No Anthropic API key provided. NLP controller will operate in basic mode.")
            self.client = None
        else:
            try:
                if Anthropic:
                    self.client = Anthropic(api_key=self.api_key)
                    logger.info("NLP controller initialized with Anthropic")
                else:
                    logger.warning("Anthropic package not installed. NLP controller will operate in basic mode.")
                    self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
    
    def process_command(self, text_input: str, trading_agent=None):
        """
        Process a natural language command and execute the corresponding action.
        
        Args:
            text_input: The natural language command from the user
            trading_agent: Reference to the trading agent object
            
        Returns:
            Response message and any action result
        """
        if not text_input.strip():
            return "Please enter a command."
        
        # Basic command processing without Anthropic
        if not self.client:
            return self._basic_command_processing(text_input, trading_agent)
        
        # Advanced NLP processing with Anthropic
        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=self._get_system_prompt(),
                messages=[{"role": "user", "content": text_input}]
            )
            
            response_text = message.content[0].text if hasattr(message, 'content') and message.content else ""
            
            # Extract command and parameters
            command_data = self._extract_command_data(response_text)
            
            if command_data:
                command_name = command_data.get("command")
                params = command_data.get("parameters", {})
                
                if command_name in self.commands:
                    handler = self.commands[command_name]
                    result = handler(params, trading_agent)
                    return f"Executed: {command_name}\n{result}"
                else:
                    return f"Unknown command: {command_name}"
            else:
                return "I couldn't understand that command. Type 'help' for available commands."
                
        except Exception as e:
            logger.error(f"Error processing command with Anthropic: {str(e)}")
            # Fall back to basic processing
            return self._basic_command_processing(text_input, trading_agent)
    
    def _get_system_prompt(self) -> str:
        """Returns the system prompt for NLP command processing."""
        return """
        You are an assistant that parses natural language commands for a Solana cryptocurrency trading platform.
        Your task is to understand the user's intent and translate it into a structured command with parameters.
        
        Available commands:
        - buy: Purchase a token
        - sell: Sell a token
        - check_price: Check the current price of a token
        - check_balance: Check wallet balance
        - show_portfolio: Display portfolio holdings
        - analyze_token: Perform technical analysis on a token
        - set_trade_limit: Set trading limits
        - help: Show available commands
        
        For each command, extract any relevant parameters like token symbol, amount, etc.
        
        Your response must be in JSON format with these keys:
        {
            "command": "[command name from the list above]",
            "parameters": {
                "token": "[token symbol if applicable]",
                "amount": "[amount if applicable]",
                ... (other relevant parameters)
            }
        }
        
        Only output the JSON object, nothing else.
        """
    
    def _extract_command_data(self, response_text: str) -> Dict:
        """
        Extract command and parameters from the API response.
        
        Args:
            response_text: The text response from Anthropic
            
        Returns:
            Dictionary with command and parameters
        """
        try:
            # Try to extract JSON from the response
            match = re.search(r'{.*}', response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error extracting command data: {str(e)}")
        
        return {}
    
    def _basic_command_processing(self, text_input: str, trading_agent) -> str:
        """
        Basic command processing without using Anthropic.
        
        Args:
            text_input: User input text
            trading_agent: Trading agent reference
            
        Returns:
            Response message
        """
        text_lower = text_input.lower().strip()
        
        # Check for basic commands
        if "buy" in text_lower:
            # Extract token and amount using regex
            token_match = re.search(r'buy\s+(\w+)', text_lower)
            amount_match = re.search(r'(\d+(\.\d+)?)', text_lower)
            
            token = token_match.group(1).upper() if token_match else "SOL"
            amount = float(amount_match.group(1)) if amount_match else 0.1
            
            return self._handle_buy({"token": token, "amount": amount}, trading_agent)
            
        elif "sell" in text_lower:
            token_match = re.search(r'sell\s+(\w+)', text_lower)
            amount_match = re.search(r'(\d+(\.\d+)?)', text_lower)
            
            token = token_match.group(1).upper() if token_match else "SOL"
            amount = float(amount_match.group(1)) if amount_match else 0.1
            
            return self._handle_sell({"token": token, "amount": amount}, trading_agent)
            
        elif "price" in text_lower or "check" in text_lower and any(token in text_lower for token in ["sol", "btc", "eth"]):
            token_match = re.search(r'(sol|btc|eth|usdt|usdc)', text_lower)
            token = token_match.group(1).upper() if token_match else "SOL"
            
            return self._handle_check_price({"token": token}, trading_agent)
            
        elif "balance" in text_lower:
            return self._handle_check_balance({}, trading_agent)
            
        elif "portfolio" in text_lower:
            return self._handle_show_portfolio({}, trading_agent)
            
        elif "analyze" in text_lower:
            token_match = re.search(r'analyze\s+(\w+)', text_lower)
            token = token_match.group(1).upper() if token_match else "SOL"
            
            return self._handle_analyze_token({"token": token}, trading_agent)
            
        elif "help" in text_lower:
            return self._handle_help({}, trading_agent)
            
        else:
            return "I couldn't understand that command. Type 'help' for available commands."
    
    def _handle_buy(self, params: Dict, trading_agent) -> str:
        """Handle buy command"""
        token = params.get("token", "SOL")
        amount = params.get("amount", 0.1)
        
        if trading_agent and hasattr(trading_agent, "execute_trade"):
            try:
                result = trading_agent.execute_trade(token, amount, is_buy=True)
                return f"Buying {amount} {token}...\n{result}"
            except Exception as e:
                return f"Error executing buy: {str(e)}"
        return f"Would buy {amount} {token} (simulation mode)"
    
    def _handle_sell(self, params: Dict, trading_agent) -> str:
        """Handle sell command"""
        token = params.get("token", "SOL")
        amount = params.get("amount", 0.1)
        
        if trading_agent and hasattr(trading_agent, "execute_trade"):
            try:
                result = trading_agent.execute_trade(token, amount, is_buy=False)
                return f"Selling {amount} {token}...\n{result}"
            except Exception as e:
                return f"Error executing sell: {str(e)}"
        return f"Would sell {amount} {token} (simulation mode)"
    
    def _handle_check_price(self, params: Dict, trading_agent) -> str:
        """Handle check price command"""
        token = params.get("token", "SOL")
        
        if trading_agent and hasattr(trading_agent, "get_token_price"):
            try:
                price = trading_agent.get_token_price(token)
                return f"Current {token} price: ${price:.4f}"
            except Exception as e:
                return f"Error checking price: {str(e)}"
        return f"Would check {token} price (simulation mode)"
    
    def _handle_check_balance(self, params: Dict, trading_agent) -> str:
        """Handle check balance command"""
        if trading_agent and hasattr(trading_agent, "wallet") and trading_agent.wallet:
            try:
                balance = trading_agent.wallet.get_balance()
                return f"Current wallet balance: {balance:.4f} SOL"
            except Exception as e:
                return f"Error checking balance: {str(e)}"
        return "Would check wallet balance (simulation mode)"
    
    def _handle_show_portfolio(self, params: Dict, trading_agent) -> str:
        """Handle show portfolio command"""
        if trading_agent and hasattr(trading_agent, "get_portfolio"):
            try:
                portfolio = trading_agent.get_portfolio()
                return f"Portfolio: {portfolio}"
            except Exception as e:
                return f"Error getting portfolio: {str(e)}"
        return "Would show portfolio (simulation mode)"
    
    def _handle_analyze_token(self, params: Dict, trading_agent) -> str:
        """Handle analyze token command"""
        token = params.get("token", "SOL")
        
        if trading_agent and hasattr(trading_agent, "analyze_token"):
            try:
                analysis = trading_agent.analyze_token(token)
                return f"Analysis for {token}: {analysis}"
            except Exception as e:
                return f"Error analyzing token: {str(e)}"
        return f"Would analyze {token} (simulation mode)"
    
    def _handle_set_trade_limit(self, params: Dict, trading_agent) -> str:
        """Handle set trade limit command"""
        limit = params.get("limit", 0.1)
        
        if trading_agent and hasattr(trading_agent, "config"):
            try:
                trading_agent.config.max_trade_amount = limit
                return f"Trade limit set to {limit} SOL"
            except Exception as e:
                return f"Error setting trade limit: {str(e)}"
        return f"Would set trade limit to {limit} SOL (simulation mode)"
    
    def _handle_help(self, params: Dict, trading_agent) -> str:
        """Handle help command"""
        return """
Available commands:
- buy [token] [amount] - Buy a token
- sell [token] [amount] - Sell a token
- check price [token] - Check current token price
- check balance - Check wallet balance
- show portfolio - Display your holdings
- analyze [token] - Analyze a token
- set trade limit [amount] - Set your max trade amount
- help - Show this help message

You can use natural language for these commands.
Examples:
- "Buy 0.5 SOL"
- "What's the price of ETH right now?"
- "Show me my portfolio"
- "Analyze BTC and give me advice"
        """
