import os
import json
import base64
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import requests

# SmolAgents imports
from smolagents import CodeAgent, WebSearchTool, InferenceClientModel, LiteLLMModel
from smolagents.tools import Tool, ToolCollection
from smolagents.vision_web_browser import VisionWebBrowser

# Solana imports
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.system_program import SYS_PROGRAM_ID, TransferParams, transfer
from solana.rpc.types import TxOpts

# Metaplex imports (assuming installed via metaplex python SDK/wrapper)
from metaplex.transactions import Metadata, MasterEdition
from metaplex.metadata import create_metadata_instruction, create_master_edition_instruction

class SolanaWallet:
    """
    A class to manage a Solana wallet for transactions and signing.
    """
    def __init__(self, keypair: Optional[Keypair] = None, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """
        Initialize the Solana wallet.
        
        Args:
            keypair: Existing Solana keypair. If None, a new one will be generated.
            rpc_url: URL of the Solana RPC endpoint.
        """
        self.rpc_url = rpc_url
        self.client = Client(rpc_url)
        self.keypair = keypair or Keypair()
        
    @classmethod
    def from_private_key(cls, private_key: List[int], rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """
        Create a wallet from a private key.
        
        Args:
            private_key: List of integers representing the private key.
            rpc_url: URL of the Solana RPC endpoint.
            
        Returns:
            SolanaWallet: A wallet initialized with the provided private key.
        """
        keypair = Keypair.from_secret_key(bytes(private_key))
        return cls(keypair, rpc_url)
    
    @classmethod
    def from_seed_phrase(cls, seed_phrase: str, passphrase: str = "", rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """
        Create a wallet from a seed phrase (mnemonic).
        
        Args:
            seed_phrase: BIP39 mnemonic seed phrase.
            passphrase: Optional passphrase for additional security.
            rpc_url: URL of the Solana RPC endpoint.
            
        Returns:
            SolanaWallet: A wallet initialized from the seed phrase.
        """
        # Implementation would depend on the specific BIP39 library used
        # This is a placeholder for the actual implementation
        import hashlib
        import hmac
        # This is a simplified example - in production use a proper BIP39 library
        seed = hashlib.pbkdf2_hmac('sha512', seed_phrase.encode('utf-8'), 
                                   ('mnemonic' + passphrase).encode('utf-8'), 
                                   2048)
        # Convert seed to keypair (simplified)
        keypair = Keypair.from_seed(seed[:32])
        return cls(keypair, rpc_url)
    
    def get_balance(self) -> int:
        """
        Get the balance of the wallet in lamports.
        
        Returns:
            int: Balance in lamports.
        """
        return self.client.get_balance(self.keypair.public_key)
    
    def transfer_sol(self, to_pubkey: PublicKey, amount_lamports: int) -> Dict:
        """
        Transfer SOL to another address.
        
        Args:
            to_pubkey: Recipient's public key.
            amount_lamports: Amount to transfer in lamports.
            
        Returns:
            Dict: Transaction result.
        """
        transfer_params = TransferParams(
            from_pubkey=self.keypair.public_key,
            to_pubkey=to_pubkey,
            lamports=amount_lamports
        )
        transaction = Transaction().add(transfer(transfer_params))
        
        # Sign and send the transaction
        result = self.client.send_transaction(
            transaction, 
            self.keypair, 
            opts=TxOpts(skip_preflight=False)
        )
        return result

class MetaplexNFT:
    """
    A class to interact with Metaplex NFTs.
    """
    def __init__(self, wallet: SolanaWallet):
        """
        Initialize the Metaplex NFT handler.
        
        Args:
            wallet: SolanaWallet instance for signing transactions.
        """
        self.wallet = wallet
        self.client = wallet.client
    
    def create_nft(self, 
                  name: str, 
                  symbol: str, 
                  uri: str, 
                  seller_fee_basis_points: int = 500, 
                  max_supply: Optional[int] = None) -> Dict:
        """
        Create a new NFT.
        
        Args:
            name: Name of the NFT.
            symbol: Symbol for the NFT.
            uri: URI pointing to the NFT metadata.
            seller_fee_basis_points: Royalty fee in basis points (100 = 1%).
            max_supply: Maximum supply for the edition (None for unlimited).
            
        Returns:
            Dict: Transaction result and NFT details.
        """
        # This is a simplified placeholder - actual implementation would use Metaplex SDK
        # or construct the proper transactions
        
        # 1. Create a new mint account (token)
        # 2. Create metadata account
        # 3. Create master edition account
        
        # Simplified example:
        transaction = Transaction()
        
        # Add necessary instructions to the transaction
        # (These would be the actual Metaplex instructions)
        
        # Sign and send the transaction
        result = self.client.send_transaction(
            transaction, 
            self.wallet.keypair, 
            opts=TxOpts(skip_preflight=False)
        )
        
        return {
            "transaction": result,
            "nft_details": {
                "name": name,
                "symbol": symbol,
                "uri": uri,
                "seller_fee_basis_points": seller_fee_basis_points,
                "max_supply": max_supply
            }
        }
    
    def fetch_nft_data(self, mint_address: PublicKey) -> Dict:
        """
        Fetch data for an NFT by its mint address.
        
        Args:
            mint_address: Public key of the NFT's mint account.
            
        Returns:
            Dict: NFT metadata and on-chain account data.
        """
        # This would use the proper Metaplex SDK methods to fetch NFT data
        # Simplified placeholder for demonstration
        pass


class AIProvider:
    """
    A class to handle interactions with various AI providers.
    """
    def __init__(self):
        """Initialize with API keys from environment variables."""
        self.api_keys = {
            "openai": os.environ.get("OPENAI_API_KEY"),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "xai": os.environ.get("XAI_API_KEY"),
            "openrouter": os.environ.get("OPEN_ROUTER_API_KEY"),
        }
        
        # Initialize model clients
        self.models = {}
        if self.api_keys["anthropic"]:
            self.models["claude"] = LiteLLMModel(
                model_id="anthropic/claude-3-opus-20240229",
                api_key=self.api_keys["anthropic"]
            )
            
        if self.api_keys["openai"]:
            self.models["gpt4"] = LiteLLMModel(
                model_id="gpt-4o",
                api_key=self.api_keys["openai"]
            )
            
        # Add default model
        self.models["default"] = InferenceClientModel(
            model_id="mistralai/Mixtral-8x7B-Instruct-v0.1"
        )
    
    def get_model(self, name: str = "default"):
        """Get an AI model by name."""
        return self.models.get(name, self.models["default"])


class BirdeyeAPI:
    """
    A class to interact with the Birdeye API for token analytics.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Birdeye API client.
        
        Args:
            api_key: Birdeye API key. If None, tries to get from environment.
        """
        self.api_key = api_key or os.environ.get("BIRDEYE_API_KEY")
        self.base_url = "https://public-api.birdeye.so"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_token_price(self, token_address: str) -> Dict:
        """
        Get price data for a token.
        
        Args:
            token_address: Solana address of the token.
            
        Returns:
            Dict: Token price information.
        """
        url = f"{self.base_url}/public/price?address={token_address}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_token_metadata(self, token_address: str) -> Dict:
        """
        Get metadata for a token.
        
        Args:
            token_address: Solana address of the token.
            
        Returns:
            Dict: Token metadata.
        """
        url = f"{self.base_url}/public/tokenlist?address={token_address}"
        response = requests.get(url, headers=self.headers)
        return response.json()


class SolanaAIAgent:
    """
    A Solana AI agent that can browse the web, interact with the Solana blockchain,
    and generate/mint NFTs using various AI models.
    """
    def __init__(self, 
                 wallet: Optional[SolanaWallet] = None,
                 rpc_url: str = "https://api.mainnet-beta.solana.com",
                 model_name: str = "default"):
        """
        Initialize the Solana AI agent.
        
        Args:
            wallet: SolanaWallet instance. If None, a new one will be generated.
            rpc_url: URL of the Solana RPC endpoint.
            model_name: Name of the AI model to use.
        """
        # Initialize wallet
        self.wallet = wallet or SolanaWallet(rpc_url=rpc_url)
        
        # Initialize AI providers
        self.ai_provider = AIProvider()
        self.model = self.ai_provider.get_model(model_name)
        
        # Initialize Metaplex handler
        self.metaplex = MetaplexNFT(self.wallet)
        
        # Initialize Birdeye API
        self.birdeye = BirdeyeAPI()
        
        # Initialize SmolAgents browser
        self.browser = VisionWebBrowser()
        
        # Set up agent with tools
        self.agent = self._setup_agent()
    
    def _setup_agent(self) -> CodeAgent:
        """
        Set up the CodeAgent with all necessary tools.
        
        Returns:
            CodeAgent: Configured agent with tools.
        """
        # Define custom tools
        @Tool("get_sol_balance")
        def get_sol_balance() -> str:
            """Get the SOL balance of the agent's wallet."""
            balance_lamports = self.wallet.get_balance()
            balance_sol = balance_lamports / 10**9  # Convert lamports to SOL
            return f"Wallet balance: {balance_sol} SOL ({balance_lamports} lamports)"
        
        @Tool("transfer_sol")
        def transfer_sol(recipient: str, amount_sol: float) -> str:
            """
            Transfer SOL to a recipient address.
            
            Args:
                recipient: Recipient's public key as a string.
                amount_sol: Amount to transfer in SOL.
                
            Returns:
                str: Transaction result.
            """
            try:
                recipient_pubkey = PublicKey(recipient)
                amount_lamports = int(amount_sol * 10**9)  # Convert SOL to lamports
                result = self.wallet.transfer_sol(recipient_pubkey, amount_lamports)
                return f"Transfer successful. Transaction signature: {result['result']}"
            except Exception as e:
                return f"Transfer failed: {str(e)}"
        
        @Tool("get_token_price")
        def get_token_price(token_address: str) -> str:
            """
            Get the current price of a token using Birdeye API.
            
            Args:
                token_address: Solana address of the token.
                
            Returns:
                str: Token price information.
            """
            try:
                price_data = self.birdeye.get_token_price(token_address)
                return f"Token price: ${price_data.get('data', {}).get('value', 'Unknown')}"
            except Exception as e:
                return f"Failed to get token price: {str(e)}"
        
        @Tool("mint_nft")
        def mint_nft(name: str, symbol: str, uri: str, royalty_percentage: float = 5.0) -> str:
            """
            Mint a new NFT.
            
            Args:
                name: Name of the NFT.
                symbol: Symbol for the NFT.
                uri: URI pointing to the NFT metadata.
                royalty_percentage: Royalty percentage (0-100).
                
            Returns:
                str: Result of the minting operation.
            """
            try:
                # Convert percentage to basis points (100 = 1%)
                seller_fee_basis_points = int(royalty_percentage * 100)
                
                result = self.metaplex.create_nft(
                    name=name,
                    symbol=symbol,
                    uri=uri,
                    seller_fee_basis_points=seller_fee_basis_points
                )
                
                return f"NFT minted successfully. Transaction signature: {result['transaction']['result']}"
            except Exception as e:
                return f"Failed to mint NFT: {str(e)}"
        
        # Create the agent with tools
        agent = CodeAgent(
            tools=[
                get_sol_balance,
                transfer_sol,
                get_token_price,
                mint_nft,
                WebSearchTool(),
            ],
            model=self.model,
            additional_authorized_imports=["helium", "requests", "json", "base64"],
            max_steps=20,
            verbosity_level=1,
        )
        
        # Import necessary modules for the agent
        agent.python_executor("import requests, json, base64", agent.state)
        
        return agent
    
    def run(self, query: str) -> str:
        """
        Run a query through the agent.
        
        Args:
            query: User query or instruction.
            
        Returns:
            str: Agent's response.
        """
        return self.agent.run(query)
    
    def browse(self, instructions: str) -> str:
        """
        Execute browser instructions using the VisionWebBrowser.
        
        Args:
            instructions: Instructions for web browsing.
            
        Returns:
            str: Result of the browsing operation.
        """
        return self.browser.run(instructions)
    
    def generate_art(self, prompt: str, output_path: Optional[str] = None) -> str:
        """
        Generate art using an AI model.
        
        Args:
            prompt: Description of the art to generate.
            output_path: Path to save the generated image. If None, returns base64 encoded image.
            
        Returns:
            str: Path to saved image or base64 encoded image.
        """
        # This is a placeholder. In a real implementation, you would:
        # 1. Call an image generation API like DALL-E or Stable Diffusion
        # 2. Process the result and save it or return it
        # 3. Potentially mint it as an NFT
        
        # Simplified example with a hypothetical image API
        try:
            # Placeholder for actual image generation code
            image_data = "base64_encoded_image_data"  # This would be the real image data
            
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(image_data))
                return f"Image saved to {output_path}"
            else:
                return f"data:image/png;base64,{image_data}"
        except Exception as e:
            return f"Failed to generate art: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Create a Solana AI agent
    agent = SolanaAIAgent()
    
    # Run a query
    result = agent.run("What is the current price of SOL?")
    print(result)
    
    # Browse the web
    browse_result = agent.browse("Go to solana.com and tell me about the latest features")
    print(browse_result)
    
    # Generate and mint an NFT
    art_result = agent.generate_art("A futuristic city with flying cars")
    print(art_result)
    
    nft_result = agent.run("Mint an NFT named 'Future City' with the symbol 'FCITY' using the generated art")
    print(nft_result)
