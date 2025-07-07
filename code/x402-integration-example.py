import os
import json
import argparse
from typing import Dict, Any, Optional

# Import components
from solana_ai_agent import SolanaAIAgent, SolanaWallet
from x402_module import X402PaymentHandler, X402HttpClient, integrate_x402_with_solana_agent

# Python Umi example
from metaplex_integration import MetaplexClient
from x402_umi_integration import createX402Client, x402Plugin

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file or environment variables.
    
    Args:
        config_path: Path to configuration file.
        
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    config = {
        "default_model": "default",
        "browser_model": "meta-llama/Llama-3.3-70B-Instruct",
        "dev_model": "anthropic/claude-3-opus-20240229",
        "headless_browser": False,
        "ollama_endpoint": os.environ.get("OLLAMA_API_BASE"),
        "auto_approve_threshold": 0.5,  # Auto-approve payments under 0.5 USDC
        "api_keys": {
            "openai": os.environ.get("OPENAI_API_KEY"),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "xai": os.environ.get("XAI_API_KEY"),
            "openrouter": os.environ.get("OPEN_ROUTER_API_KEY"),
            "birdeye": os.environ.get("BIRDEYE_API_KEY"),
        }
    }
    
    # Load from file if provided
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                
                # Update config with file values
                for key, value in file_config.items():
                    if key == "api_keys" and isinstance(value, dict):
                        config["api_keys"].update(value)
                    else:
                        config[key] = value
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    
    return config

def load_wallet(wallet_path: Optional[str] = None, rpc_url: str = "https://api.mainnet-beta.solana.com") -> SolanaWallet:
    """
    Load a Solana wallet from a keypair file or create a new one.
    
    Args:
        wallet_path: Path to wallet keypair file.
        rpc_url: URL of the Solana RPC endpoint.
        
    Returns:
        SolanaWallet: Initialized wallet.
    """
    if wallet_path and os.path.exists(wallet_path):
        try:
            with open(wallet_path, 'r') as f:
                keypair_bytes = json.load(f)
            return SolanaWallet.from_private_key(keypair_bytes, rpc_url)
        except Exception as e:
            print(f"Warning: Failed to load wallet from {wallet_path}: {e}")
            print("Creating a new wallet instead.")
    
    # Create a new wallet if no valid wallet provided
    return SolanaWallet(rpc_url=rpc_url)

def setup_python_x402_example(config_path: Optional[str] = None, wallet_path: Optional[str] = None):
    """
    Set up an example using the Python x402 integration.
    
    Args:
        config_path: Path to configuration file.
        wallet_path: Path to wallet keypair file.
    """
    # Load configuration
    config = load_config(config_path)
    
    # Initialize wallet
    wallet = load_wallet(wallet_path)
    
    # Print wallet info
    print(f"Wallet address: {wallet.keypair.public_key}")
    print(f"SOL balance: {wallet.get_balance() / 1e9} SOL")
    
    # Create SolanaAI agent
    agent = SolanaAIAgent(
        wallet=wallet,
        model_name=config.get("default_model", "default")
    )
    
    # Integrate x402 with the agent
    payment_handler, http_client = integrate_x402_with_solana_agent(
        agent,
        wallet,
        auto_approve_threshold=config.get("auto_approve_threshold", 0.1)
    )
    
    # Example of accessing a premium API with x402
    print("\nAttempting to access a premium API with x402 payment protocol...")
    premium_api_url = "https://s402.w3hf.fun/api/premium-data"
    
    # Use the agent's x402 tool to make the request
    result = agent.agent.python_executor(f"""
x402_request("{premium_api_url}")
    """, agent.agent.state)
    
    print(f"API request result: {json.dumps(result, indent=2)}")
    
    # Show payment history
    print("\nPayment history:")
    for payment in payment_handler.payment_history:
        print(f" - {payment['timestamp']}: {payment['amount']} {payment['token']} to {payment['recipient']}")
    
    return agent, payment_handler, http_client

def setup_typescript_x402_example(config_path: Optional[str] = None, wallet_path: Optional[str] = None):
    """
    Set up an example using the TypeScript x402 integration with Umi.
    
    Args:
        config_path: Path to configuration file.
        wallet_path: Path to wallet keypair file.
    """
    # Load configuration
    config = load_config(config_path)
    
    # Initialize wallet
    wallet = load_wallet(wallet_path)
    
    # Print wallet info
    print(f"Wallet address: {wallet.keypair.public_key}")
    print(f"SOL balance: {wallet.get_balance() / 1e9} SOL")
    
    # Create MetaplexClient
    metaplex_client = MetaplexClient(rpc_url="https://api.mainnet-beta.solana.com", keypair=wallet.keypair)
    
    # Add x402 plugin to Umi
    # This would actually be done in JavaScript/TypeScript as follows:
    # 
    # import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
    # import { mplTokenMetadata } from '@metaplex-foundation/mpl-token-metadata';
    # import { x402Plugin } from './x402-umi-integration';
    # 
    # const umi = createUmi('https://api.mainnet-beta.solana.com')
    #   .use(mplTokenMetadata())
    #   .use(x402Plugin({
    #     autoApproveThreshold: 0.1,
    #   }));
    # 
    # // Make a request with x402 payment support
    # const response = await umi.x402.request('https://api.example.com/premium-content');
    # console.log(response.body);
    
    print("\nTypeScript/Umi integration would be used in a JavaScript/TypeScript environment.")
    print("See the implementation in x402-umi-integration.ts for details.")
    
    # Dummy code to show how it would be used
    print("\nExample usage in TypeScript:")
    print("""
import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { mplTokenMetadata } from '@metaplex-foundation/mpl-token-metadata';
import { x402Plugin } from './x402-umi-integration';

// Create UMI instance with x402 plugin
const umi = createUmi('https://api.mainnet-beta.solana.com')
  .use(mplTokenMetadata())
  .use(x402Plugin({
    autoApproveThreshold: 0.1,
  }));

// Make a request with x402 payment support
async function fetchPremiumContent() {
  try {
    const response = await umi.x402.request('https://api.example.com/premium-content');
    console.log('Response:', response.body);
    
    // Check payment history
    const paymentHistory = umi.x402.getPaymentHistory();
    console.log('Payment history:', paymentHistory);
  } catch (error) {
    console.error('Request failed:', error);
  }
}

fetchPremiumContent();
    """)
    
    return metaplex_client

def run_cli():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(description="X402 Payment Protocol Examples")
    
    # General arguments
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--wallet", type=str, help="Path to wallet keypair file")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Python example command
    python_parser = subparsers.add_parser("python", help="Run Python x402 example")
    
    # TypeScript example command
    ts_parser = subparsers.add_parser("typescript", help="Show TypeScript x402 example")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run appropriate example
    if args.command == "python":
        agent, payment_handler, http_client = setup_python_x402_example(args.config, args.wallet)
        
        # Clean up
        print("\nCleaning up...")
        # Close any resources if needed
        
    elif args.command == "typescript":
        metaplex_client = setup_typescript_x402_example(args.config, args.wallet)
        
        # No cleanup needed for this example
        
    else:
        # No command specified, print help
        parser.print_help()

if __name__ == "__main__":
    run_cli()
