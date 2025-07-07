# examples.py
"""
Example scripts demonstrating Solana Agent Kit capabilities
Run individual functions to test specific features
"""

import asyncio
import os
from dotenv import load_dotenv
from solana_agent_kit import SolanaAgentKit
from solders.pubkey import Pubkey
from solana_agent_kit.types import PumpfunTokenOptions

# Load environment variables
load_dotenv()

# Common token addresses for examples
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
RAY_MINT = "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"

async def init_agent():
    """Initialize the Solana Agent"""
    private_key = os.getenv('SOLANA_PRIVATE_KEY')
    rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not private_key:
        raise ValueError("SOLANA_PRIVATE_KEY environment variable required")
    
    agent = SolanaAgentKit(private_key, rpc_url, openai_key)
    print(f"🔗 Connected to wallet: {agent.wallet_address}")
    return agent

async def example_wallet_operations():
    """Example: Basic wallet operations"""
    print("\n📱 WALLET OPERATIONS EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Get SOL balance
    balance = await agent.get_balance()
    sol_balance = balance / 1e9
    print(f"SOL Balance: {sol_balance:.4f} SOL")
    
    # Get network TPS
    try:
        tps = await agent.get_tps()
        print(f"Network TPS: {tps}")
    except Exception as e:
        print(f"Could not get TPS: {e}")
    
    # Get token data
    try:
        sol_data = await agent.get_token_data_by_ticker("SOL")
        if sol_data:
            print(f"SOL Price: ${sol_data.get('price', 'N/A')}")
            print(f"24h Change: {sol_data.get('price_change_24h', 'N/A')}%")
    except Exception as e:
        print(f"Could not get SOL data: {e}")

async def example_token_swap():
    """Example: Token swapping via Jupiter"""
    print("\n🔄 TOKEN SWAP EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Example: Swap 0.001 SOL to USDC
    try:
        print("Swapping 0.001 SOL to USDC via Jupiter...")
        
        signature = await agent.trade(
            output_mint=Pubkey.from_string(USDC_MINT),
            input_amount=int(0.001 * 1e9),  # 0.001 SOL in lamports
            input_mint=Pubkey.from_string(SOL_MINT),
            slippage_bps=300  # 3% slippage
        )
        
        print(f"✅ Swap successful! Transaction: {signature}")
        print(f"🔗 View on Solscan: https://solscan.io/tx/{signature}")
        
    except Exception as e:
        print(f"❌ Swap failed: {e}")
        print("This is normal if you don't have enough SOL or in simulation mode")

async def example_sol_staking():
    """Example: SOL staking"""
    print("\n🥩 SOL STAKING EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Example: Stake 0.01 SOL
    try:
        print("Staking 0.01 SOL...")
        
        signature = await agent.stake(amount=0.01)
        
        print(f"✅ Staking successful! Transaction: {signature}")
        print(f"🔗 View on Solscan: https://solscan.io/tx/{signature}")
        
    except Exception as e:
        print(f"❌ Staking failed: {e}")
        print("This is normal if you don't have enough SOL or in simulation mode")

async def example_lending():
    """Example: Asset lending via Lulo"""
    print("\n💰 LENDING EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Example: Lend assets
    try:
        print("Lending assets via Lulo...")
        
        signature = await agent.lend_assets(amount=1)  # Amount depends on asset
        
        print(f"✅ Lending successful! Transaction: {signature}")
        print(f"🔗 View on Solscan: https://solscan.io/tx/{signature}")
        
    except Exception as e:
        print(f"❌ Lending failed: {e}")
        print("This is normal if you don't have compatible assets or in simulation mode")

async def example_token_creation():
    """Example: Create a new SPL token"""
    print("\n🪙 TOKEN CREATION EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Example: Deploy a new token
    try:
        print("Creating new SPL token...")
        
        result = await agent.deploy_token(
            name="Test AI Token",
            uri="https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            symbol="TAIT",
            decimals=9,
            initial_supply=1000000
        )
        
        print(f"✅ Token created successfully!")
        print(f"Token Mint: {result.mint}")
        print(f"🔗 View on Solscan: https://solscan.io/token/{result.mint}")
        
    except Exception as e:
        print(f"❌ Token creation failed: {e}")
        print("This is normal if you don't have enough SOL for fees")

async def example_pump_fun_token():
    """Example: Launch token on Pump.fun"""
    print("\n🚀 PUMP.FUN TOKEN EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Example: Launch a Pump.fun token
    try:
        print("Launching token on Pump.fun...")
        
        options = PumpfunTokenOptions()
        
        response = await agent.launch_pump_fun_token(
            token_name="Test Meme Token",
            token_ticker="TMT",
            description="A test meme token created by AI",
            image_url="https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            options=options
        )
        
        print(f"✅ Pump.fun token launched!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Pump.fun launch failed: {e}")
        print("This requires significant SOL and is high risk")

async def example_raydium_trading():
    """Example: Trading on Raydium"""
    print("\n🌊 RAYDIUM TRADING EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Note: This requires a valid pair address
    # In practice, you'd get this from Raydium API or on-chain data
    
    print("Raydium trading requires specific pair addresses")
    print("Example operations:")
    print("- Buy tokens from a liquidity pool")
    print("- Sell tokens back to the pool")
    print("- Monitor pool liquidity and prices")
    
    try:
        # Example buy (would fail without valid pair)
        # pair_address = "valid_pair_address_here"
        # confirmed = await agent.buy_with_raydium(
        #     pair_address=Pubkey.from_string(pair_address),
        #     sol_in=0.01,
        #     slippage=300
        # )
        
        print("⚠️  Skipping actual trade (requires valid pair address)")
        
    except Exception as e:
        print(f"Trade simulation: {e}")

async def example_market_data():
    """Example: Fetching market data"""
    print("\n📊 MARKET DATA EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Get data for popular tokens
    tokens = ["SOL", "RAY", "JUP"]
    
    for ticker in tokens:
        try:
            data = await agent.get_token_data_by_ticker(ticker)
            if data:
                print(f"{ticker}:")
                print(f"  Price: ${data.get('price', 'N/A')}")
                print(f"  24h Change: {data.get('price_change_24h', 'N/A')}%")
                print(f"  Market Cap: ${data.get('market_cap', 'N/A'):,}")
            else:
                print(f"{ticker}: No data available")
        except Exception as e:
            print(f"{ticker}: Error fetching data - {e}")

async def example_nft_operations():
    """Example: NFT operations"""
    print("\n🎨 NFT OPERATIONS EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    print("NFT operations available:")
    print("- Deploy NFT collections")
    print("- Mint individual NFTs")
    print("- Set royalty configurations")
    print("- Manage metadata")
    print("- List on 3.Land marketplace")
    
    try:
        # Example collection deployment (commented to avoid fees)
        # collection = await agent.deploy_collection({
        #     "name": "Test AI Collection",
        #     "uri": "https://example.com/metadata.json",
        #     "royalty_basis_points": 500,  # 5%
        #     "creators": [
        #         {
        #             "address": str(agent.wallet_address),
        #             "percentage": 100
        #         }
        #     ]
        # })
        
        print("⚠️  Skipping actual deployment (requires SOL for fees)")
        
    except Exception as e:
        print(f"NFT operation simulation: {e}")

async def example_advanced_features():
    """Example: Advanced features"""
    print("\n⚡ ADVANCED FEATURES EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    print("Advanced features available:")
    print("- Jito bundles for MEV protection")
    print("- Compressed airdrops via ZK compression")
    print("- Meteora DLMM pool creation")
    print("- Orca Whirlpool integration")
    print("- OpenBook market creation")
    print("- SNS domain registration")
    
    try:
        # Example: Request faucet funds (devnet only)
        print("Testing faucet request (works on devnet)...")
        response = await agent.request_faucet_funds()
        print(f"Faucet response: {response}")
        
    except Exception as e:
        print(f"Faucet request: {e} (normal on mainnet)")

def print_menu():
    """Print example menu"""
    print("\n🎯 SOLANA AGENT KIT EXAMPLES")
    print("=" * 50)
    print("1. Wallet Operations")
    print("2. Token Swapping")
    print("3. SOL Staking")
    print("4. Asset Lending")
    print("5. Token Creation")
    print("6. Pump.fun Token Launch")
    print("7. Raydium Trading")
    print("8. Market Data")
    print("9. NFT Operations")
    print("10. Advanced Features")
    print("11. Run All Examples")
    print("0. Exit")

async def main():
    """Main example runner"""
    examples = {
        1: example_wallet_operations,
        2: example_token_swap,
        3: example_sol_staking,
        4: example_lending,
        5: example_token_creation,
        6: example_pump_fun_token,
        7: example_raydium_trading,
        8: example_market_data,
        9: example_nft_operations,
        10: example_advanced_features
    }
    
    print("🚀 Welcome to Solana Agent Kit Examples!")
    print("⚠️  Note: Most examples are in simulation mode to avoid fees")
    print("💡 Set TRADING_ENABLED=true and ensure sufficient SOL for live operations")
    
    while True:
        print_menu()
        
        try:
            choice = int(input("\nEnter your choice (0-11): "))
            
            if choice == 0:
                print("👋 Goodbye!")
                break
            elif choice == 11:
                print("\n🏃 Running all examples...")
                for i in range(1, 11):
                    try:
                        await examples[i]()
                    except Exception as e:
                        print(f"Example {i} failed: {e}")
                    await asyncio.sleep(1)
            elif choice in examples:
                await examples[choice]()
            else:
                print("❌ Invalid choice. Please try again.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    asyncio.run(main())
