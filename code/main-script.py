import os
import argparse
import json
from typing import Optional, Dict, Any, List, Union

# Import the components from our modules
from solana_ai_agent import SolanaAIAgent, SolanaWallet, MetaplexNFT
from solana_agent_browser_module import SolanaWebBrowser, SolanaDeveloperBrowser

class SolanaChainAI:
    """
    Integrated AI system for Solana blockchain interaction, combining browser automation,
    on-chain transactions, and AI-powered metadata generation.
    """
    
    def __init__(self, 
                config_path: Optional[str] = None, 
                wallet_path: Optional[str] = None,
                rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """
        Initialize the SolanaChainAI system.
        
        Args:
            config_path: Path to configuration file with API keys.
            wallet_path: Path to wallet keypair file.
            rpc_url: URL of the Solana RPC endpoint.
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize wallet
        self.wallet = self._init_wallet(wallet_path, rpc_url)
        
        # Initialize components
        self.agent = SolanaAIAgent(
            wallet=self.wallet,
            rpc_url=rpc_url,
            model_name=self.config.get("default_model", "default")
        )
        
        self.browser = SolanaWebBrowser(
            headless=self.config.get("headless_browser", False),
            model_id=self.config.get("browser_model", "meta-llama/Llama-3.3-70B-Instruct"),
            api_key=self._get_api_key_for_model(self.config.get("browser_model", ""))
        )
        
        self.dev_browser = SolanaDeveloperBrowser(
            headless=self.config.get("headless_browser", False),
            model_id=self.config.get("dev_model", "anthropic/claude-3-opus-20240229"),
            api_key=self._get_api_key_for_model(self.config.get("dev_model", ""))
        )
        
        # Set local Ollama endpoint if provided
        if self.config.get("ollama_endpoint"):
            os.environ["OLLAMA_API_BASE"] = self.config["ollama_endpoint"]
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
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
    
    def _init_wallet(self, wallet_path: Optional[str] = None, rpc_url: str = "https://api.mainnet-beta.solana.com") -> SolanaWallet:
        """
        Initialize Solana wallet from a keypair file or create a new one.
        
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
    
    def _get_api_key_for_model(self, model_id: str) -> Optional[str]:
        """
        Get the appropriate API key for a model.
        
        Args:
            model_id: ID of the model.
            
        Returns:
            Optional[str]: API key for the model, if available.
        """
        model_id = model_id.lower()
        
        if "anthropic" in model_id or "claude" in model_id:
            return self.config["api_keys"].get("anthropic")
        elif "openai" in model_id or "gpt" in model_id:
            return self.config["api_keys"].get("openai")
        elif "xai" in model_id:
            return self.config["api_keys"].get("xai")
        elif "llama" in model_id or "mistral" in model_id:
            return self.config["api_keys"].get("openrouter")
        
        return None
    
    def query(self, prompt: str) -> str:
        """
        Run a general query through the main agent.
        
        Args:
            prompt: User query or instruction.
            
        Returns:
            str: Agent's response.
        """
        return self.agent.run(prompt)
    
    def browse(self, instructions: str, developer_mode: bool = False) -> str:
        """
        Execute browser instructions using the appropriate browser.
        
        Args:
            instructions: Instructions for web browsing.
            developer_mode: Whether to use the developer browser.
            
        Returns:
            str: Result of the browsing operation.
        """
        if developer_mode:
            return self.dev_browser.run(instructions)
        else:
            return self.browser.run(instructions)
    
    def explore_docs(self, program_library: str) -> str:
        """
        Explore documentation for a specific Solana program or library.
        
        Args:
            program_library: Name of the program or library.
            
        Returns:
            str: Extracted information from documentation.
        """
        instructions = f"""
        Search for documentation about {program_library} on Solana. 
        Go to the official documentation page if possible.
        Extract the most important information, including:
        - Main features and capabilities
        - Code examples
        - API methods
        - Common usage patterns
        """
        
        return self.dev_browser.run(instructions)
    
    def get_token_info(self, token_address_or_symbol: str) -> Dict[str, Any]:
        """
        Get information about a token by address or symbol.
        
        Args:
            token_address_or_symbol: Token address or symbol.
            
        Returns:
            Dict[str, Any]: Token information.
        """
        # Check if it's an address
        if token_address_or_symbol.startswith(("0x", "1", "2", "3", "4", "5", "6", "7", "8", "9")) and len(token_address_or_symbol) > 30:
            # It's likely an address, use the birdeye API directly
            instructions = f"""
            Use the get_token_price tool to get information about the token with address {token_address_or_symbol}.
            """
            result = self.agent.run(instructions)
            return {"result": result, "source": "BirdEye API"}
        else:
            # It's a symbol, search for it on Solscan
            instructions = f"""
            Go to solscan.io and search for token symbol {token_address_or_symbol}.
            Click on the first result that appears to be the main token.
            Extract all available token information using the extract_token_info tool.
            """
            result = self.browser.run(instructions)
            return {"result": result, "source": "Browser"}
    
    def generate_and_mint_nft(self, prompt: str) -> Dict[str, Any]:
        """
        Generate art and mint it as an NFT.
        
        Args:
            prompt: Description of the art to generate.
            
        Returns:
            Dict[str, Any]: Result of the NFT minting operation.
        """
        # Generate art
        art_result = self.agent.generate_art(prompt)
        
        # Mint NFT
        nft_instruction = f"""
        Mint an NFT with the following details:
        - Name: AI-generated art from "{prompt}"
        - Symbol: AIGEN
        - URI: {art_result if art_result.startswith('http') or art_result.startswith('data:') else 'https://example.com/metadata.json'}
        - Royalty: 5%
        """
        
        nft_result = self.agent.run(nft_instruction)
        
        return {
            "prompt": prompt,
            "art_result": art_result,
            "nft_result": nft_result
        }
    
    def analyze_and_extract(self, url: str) -> Dict[str, Any]:
        """
        Analyze a website and extract relevant information.
        
        Args:
            url: URL to analyze.
            
        Returns:
            Dict[str, Any]: Extracted information.
        """
        # Determine if it's a documentation site, token explorer, or NFT marketplace
        if "docs" in url or "documentation" in url or "guide" in url:
            # Developer documentation
            instructions = f"""
            Go to {url}
            Analyze the documentation and extract:
            - Main concepts
            - Code examples
            - API methods
            - Usage patterns
            """
            result = self.dev_browser.run(instructions)
            return {"result": result, "type": "documentation"}
            
        elif "solscan" in url or "birdeye" in url or "explorer" in url:
            # Token explorer
            instructions = f"""
            Go to {url}
            Analyze the token information and extract all available data using the extract_token_info tool.
            """
            result = self.browser.run(instructions)
            return {"result": result, "type": "token"}
            
        elif "magiceden" in url or "tensor" in url or "nft" in url:
            # NFT marketplace
            instructions = f"""
            Go to {url}
            Analyze the NFT information and extract all available data using the extract_nft_info tool.
            """
            result = self.browser.run(instructions)
            return {"result": result, "type": "nft"}
            
        else:
            # Generic website
            instructions = f"""
            Go to {url}
            Analyze the website and extract all relevant information about Solana, tokens, NFTs, or blockchain technology.
            """
            result = self.browser.run(instructions)
            return {"result": result, "type": "generic"}
    
    def close(self):
        """Close all browsers and resources."""
        self.browser.close()
        self.dev_browser.close()


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(description="SolanaChainAI - AI-powered Solana blockchain interaction")
    
    # General arguments
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--wallet", type=str, help="Path to wallet keypair file")
    parser.add_argument("--rpc", type=str, default="https://api.mainnet-beta.solana.com", help="Solana RPC endpoint URL")
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Run a general query")
    query_parser.add_argument("prompt", type=str, help="Query prompt")
    
    # Browse command
    browse_parser = subparsers.add_parser("browse", help="Browse the web")
    browse_parser.add_argument("instructions", type=str, help="Browser instructions")
    browse_parser.add_argument("--dev", action="store_true", help="Use developer browser")
    
    # Explore docs command
    docs_parser = subparsers.add_parser("explore-docs", help="Explore program documentation")
    docs_parser.add_argument("library", type=str, help="Program or library name")
    
    # Token info command
    token_parser = subparsers.add_parser("token-info", help="Get token information")
    token_parser.add_argument("token", type=str, help="Token address or symbol")
    
    # Mint NFT command
    nft_parser = subparsers.add_parser("mint-nft", help="Generate and mint an NFT")
    nft_parser.add_argument("prompt", type=str, help="Art description prompt")
    
    # Analyze URL command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a website")
    analyze_parser.add_argument("url", type=str, help="URL to analyze")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create SolanaChainAI instance
    solana_ai = SolanaChainAI(
        config_path=args.config,
        wallet_path=args.wallet,
        rpc_url=args.rpc
    )
    
    try:
        # Execute command
        if args.command == "query":
            result = solana_ai.query(args.prompt)
            print(result)
            
        elif args.command == "browse":
            result = solana_ai.browse(args.instructions, args.dev)
            print(result)
            
        elif args.command == "explore-docs":
            result = solana_ai.explore_docs(args.library)
            print(result)
            
        elif args.command == "token-info":
            result = solana_ai.get_token_info(args.token)
            print(json.dumps(result, indent=2))
            
        elif args.command == "mint-nft":
            result = solana_ai.generate_and_mint_nft(args.prompt)
            print(json.dumps(result, indent=2))
            
        elif args.command == "analyze":
            result = solana_ai.analyze_and_extract(args.url)
            print(json.dumps(result, indent=2))
            
        else:
            # No command specified, print help
            parser.print_help()
            
    finally:
        # Clean up resources
        solana_ai.close()


if __name__ == "__main__":
    main()
