#!/usr/bin/env python3
"""
Command-line NLP interface for the Solana Trading Desktop
with integrated risk analysis
"""
import os
import sys
import logging
import argparse
import threading
import time
from dotenv import load_dotenv

# Add the current directory to PATH for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import local modules
from nlp_controller import NLPController

# Import risk analysis modules if available
try:
    from risk_reasoning import RiskReasoningEngine
    HAS_RISK_ANALYZER = True
except ImportError:
    HAS_RISK_ANALYZER = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Attempt to import the trading desktop modules
try:
    from solana_trading_desktop import TradingAgent, TradingConfig, SOLANA_AVAILABLE
    HAS_TRADING_DESKTOP = True
except ImportError as e:
    logger.warning(f"Error importing trading desktop: {e}")
    HAS_TRADING_DESKTOP = False

def main():
    """Main entry point for the NLP interface"""
    parser = argparse.ArgumentParser(description="Solana Trading Desktop NLP Interface")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode without UI")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        logger.warning("No Anthropic API key found. Basic NLP processing will be used.")
        
    solana_tracker_api_key = os.getenv("SOLANA_TRACKER_API_KEY")
    if not solana_tracker_api_key:
        logger.warning("No Solana Tracker API key found. Risk analysis will be simulated.")
    
    # Initialize the NLP controller
    nlp = NLPController(api_key=anthropic_api_key)
    
    # Initialize risk analysis engine if available
    risk_engine = None
    if HAS_RISK_ANALYZER:
        try:
            risk_engine = RiskReasoningEngine(
                tracker_api_key=solana_tracker_api_key,
                anthropic_api_key=anthropic_api_key
            )
            logger.info("Risk analysis engine initialized")
        except Exception as e:
            logger.error(f"Error initializing risk analysis engine: {e}")
    
    # Initialize trading agent if available
    agent = None
    if HAS_TRADING_DESKTOP:
        try:
            config = TradingConfig(
                max_trade_amount=0.01,
                max_daily_trades=5,
                trading_enabled=False,  # Default to simulation mode
                min_confidence_score=0.8
            )
            agent = TradingAgent(config)
            
            # Start trading in a separate thread
            trading_thread = None
            
            if not args.headless and hasattr(agent, 'start_trading'):
                def start_trading_thread():
                    try:
                        stream_url, width, height = agent.start_trading()
                        logger.info(f"Trading desktop started. Access UI at: {stream_url}")
                    except Exception as e:
                        logger.error(f"Error starting trading: {e}")
                
                trading_thread = threading.Thread(target=start_trading_thread)
                trading_thread.daemon = True
                trading_thread.start()
                # Give it time to start
                time.sleep(5)
            
            logger.info(f"Trading agent initialized{'in headless mode' if args.headless else ''}")
        except Exception as e:
            logger.error(f"Error initializing trading agent: {e}")
            agent = None
    
    print("\n" + "=" * 60)
    print("🤖 Solana Trading Desktop NLP Interface with Risk Analysis 🤖")
    print("=" * 60)
    print("Type your trading commands in natural language")
    print("For example: 'buy 0.1 SOL' or 'check the current price of ETH'")
    if HAS_RISK_ANALYZER and risk_engine:
        print("Risk analysis: 'analyze risk for TOKEN' or 'is TOKEN safe to trade?'")
    print("Type 'help' for available commands or 'exit' to quit")
    print("=" * 60 + "\n")
    
    # Command loop
    while True:
        try:
            user_input = input("💬 Command: ")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
            
            # Check for risk analysis commands
            if HAS_RISK_ANALYZER and risk_engine and ("risk" in user_input.lower() or "safe to trade" in user_input.lower()):
                # Extract token from user input
                import re
                token_match = re.search(r'(sol|btc|eth|usdc|usdt|\w+)', user_input.lower())
                token = token_match.group(1).upper() if token_match else "SOL"
                
                # Use a mock address for demonstration
                token_address = "So11111111111111111111111111111111111111112"
                if token != "SOL":
                    # Use hash of token name as mock address
                    import hashlib
                    hash_obj = hashlib.sha256(token.encode())
                    token_address = hash_obj.hexdigest()[:32] + "pump"
                
                print(f"Analyzing risk for {token}...")
                try:
                    recommendation = risk_engine.get_trading_recommendation(token, token_address, 0.1)
                    
                    response = f"\n📊 RISK ANALYSIS FOR {token} 📊\n"
                    response += f"Recommendation: {recommendation['recommendation']}\n"
                    response += f"Risk Score: {recommendation['risk_score']}/10\n"
                    response += f"Explanation: {recommendation['explanation']}\n"
                    
                    if recommendation['ai_reasoning']:
                        response += f"\nAI Reasoning:\n{recommendation['ai_reasoning']}\n"
                        
                    if recommendation['risk_factors']:
                        response += "\nRisk Factors:\n"
                        for factor in recommendation['risk_factors'][:3]:  # Show top 3 factors
                            response += f"- {factor.get('name', 'Unknown')}\n"
                except Exception as e:
                    response = f"Error performing risk analysis: {str(e)}"
            else:
                response = nlp.process_command(user_input, agent)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            print(f"Error: {e}")
    
    # Cleanup
    if agent and hasattr(agent, 'stop_trading'):
        try:
            agent.stop_trading()
            logger.info("Trading agent stopped")
        except Exception as e:
            logger.error(f"Error stopping trading agent: {e}")
    
    print("\nThank you for using the Solana Trading Desktop NLP Interface. Goodbye!")

if __name__ == "__main__":
    main()
