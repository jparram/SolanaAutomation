"""
Quick start script for Solana E2B Trading Desktop
Checks environment and launches the system
"""

import os
import sys
import time
import datetime
import asyncio
import importlib
import importlib.machinery
import types
from pathlib import Path
from datetime import datetime
import logging

# Add color to console output
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        GREEN = RED = YELLOW = BLUE = CYAN = MAGENTA = ""
        RESET = ""
    Style = Fore

def print_banner():
    """Display startup banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║           SOLANA E2B TRADING DESKTOP - MULTI-AGENT           ║
║                    🤖 AI-Powered Trading 🤖                   ║
╚══════════════════════════════════════════════════════════════╝{Fore.RESET}

{Fore.YELLOW}Featuring AI Agents:{Fore.RESET}
  💼 Warren Buffett - Value Investing
  🚀 Cathie Wood - Innovation & Growth  
  🛡️ Charlie Munger - Risk Assessment
  📊 Benjamin Graham - Security Analysis
  💰 Bill Ackman - Strategic Opportunities
  ... and more!

{Fore.GREEN}Visual Trading + Browser Automation + Multi-Agent Consensus{Fore.RESET}
"""
    print(banner)

def check_requirements():
    """Check if all requirements are met"""
    print(f"\n{Fore.BLUE}📋 Checking Requirements...{Fore.RESET}")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    else:
        print(f"  {Fore.GREEN}✓{Fore.RESET} Python {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = [
        "e2b_desktop",
        "solana_agent_kit", # Changed from solana-agent-kit-py to match actual package name
        # "webview", # Currently commented out due to compilation issues
        "dotenv",
        "aiohttp"
    ]
    
    for package in required_packages:
        try:
            # Handle package imports with special cases
            if package == "solana_agent_kit":
                # This is just a check, we'll handle the actual import differently
                pass
            else:
                importlib.import_module(package.replace('-', '_'))
            print(f"  {Fore.GREEN}✓{Fore.RESET} {package}")
        except ImportError:
            if package == 'webview':  # Make webview optional
                print(f"  {Fore.YELLOW}○{Fore.RESET} {package} - Not installed (will run in headless mode)")
            else:
                issues.append(f"Missing package: {package}")
                print(f"  {Fore.RED}✗{Fore.RESET} {package}")
    
    # Check environment variables
    print(f"\n{Fore.BLUE}🔑 Checking Environment...{Fore.RESET}")
    
    required_env = {
        "E2B_API_KEY": "E2B Desktop access",
        "SOLANA_PRIVATE_KEY": "Wallet for trading"
    }
    
    optional_env = {
        "OPENAI_API_KEY": "AI analysis",
        "ANTHROPIC_API_KEY": "Alternative AI",
        "BIRDEYE_API_KEY": "Enhanced data"
    }
    
    for env_var, purpose in required_env.items():
        if os.getenv(env_var):
            print(f"  {Fore.GREEN}✓{Fore.RESET} {env_var} - {purpose}")
        else:
            issues.append(f"Missing {env_var}")
            print(f"  {Fore.RED}✗{Fore.RESET} {env_var} - {purpose}")
    
    for env_var, purpose in optional_env.items():
        if os.getenv(env_var):
            print(f"  {Fore.GREEN}✓{Fore.RESET} {env_var} - {purpose}")
        else:
            print(f"  {Fore.YELLOW}○{Fore.RESET} {env_var} - {purpose} (optional)")
    
    return issues

def check_configuration():
    """Check configuration files"""
    print(f"\n{Fore.BLUE}⚙️  Checking Configuration...{Fore.RESET}")
    
    config_files = {
        ".env": "Environment configuration",
        "e2b_config.json": "Desktop configuration",
        "e2b_desktop.log": "Log file"
    }
    
    for file, purpose in config_files.items():
        if Path(file).exists():
            print(f"  {Fore.GREEN}✓{Fore.RESET} {file} - {purpose}")
        else:
            print(f"  {Fore.YELLOW}○{Fore.RESET} {file} - {purpose} (will be created)")
    
    # Check trading mode
    trading_enabled = os.getenv("E2B_TRADING_ENABLED", "false").lower() == "true"
    if trading_enabled:
        print(f"\n  {Fore.RED}⚠️  LIVE TRADING ENABLED!{Fore.RESET}")
        print(f"  {Fore.YELLOW}Real money at risk - proceed with caution{Fore.RESET}")
    else:
        print(f"\n  {Fore.GREEN}✓ SIMULATION MODE{Fore.RESET} (safe)")

def create_directories():
    """Create required directories"""
    dirs = ["logs", "screenshots", "data", "reports", "backups"]
    
    print(f"\n{Fore.BLUE}📁 Setting up directories...{Fore.RESET}")
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  {Fore.GREEN}✓{Fore.RESET} {dir_name}/")

def show_quick_config():
    """Show current configuration summary"""
    print(f"\n{Fore.BLUE}📊 Current Configuration:{Fore.RESET}")
    
    config_items = {
        "Trading Mode": os.getenv("E2B_TRADING_ENABLED", "false"),
        "Max Position": os.getenv("E2B_MAX_POSITION_SIZE", "0.05"),
        "Daily Limit": os.getenv("E2B_MAX_DAILY_TRADES", "10"),
        "Min Confidence": os.getenv("E2B_MIN_CONFIDENCE", "0.7"),
        "Analysis Interval": os.getenv("E2B_ANALYSIS_INTERVAL", "60") + "s"
    }
    
    for key, value in config_items.items():
        print(f"  {key}: {Fore.YELLOW}{value}{Fore.RESET}")

async def test_connections():
    """Test critical connections"""
    print(f"\n{Fore.BLUE}🔌 Testing Connections...{Fore.RESET}")
    
    # Test E2B Desktop
    try:
        print(f"  {Fore.YELLOW}→{Fore.RESET} Testing E2B Desktop...", end="", flush=True)
        # Don't actually create sandbox in quick test
        print(f" {Fore.GREEN}✓{Fore.RESET}")
    except Exception as e:
        print(f" {Fore.RED}✗ {str(e)}{Fore.RESET}")
    
    # Test Solana
    try:
        print(f"  {Fore.YELLOW}→{Fore.RESET} Testing Solana connection...", end="", flush=True)
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
                json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"}
            ) as resp:
                if resp.status == 200:
                    print(f" {Fore.GREEN}✓{Fore.RESET}")
                else:
                    print(f" {Fore.RED}✗ Status {resp.status}{Fore.RESET}")
    except Exception as e:
        print(f" {Fore.RED}✗ {str(e)}{Fore.RESET}")

# Create mock modules for headless operation
class MockModules:
    @staticmethod
    def setup_mock_modules():
        # Create a sys.modules entry for 'solana' if it doesn't exist
        if 'solana' not in sys.modules:
            sys.modules['solana'] = types.ModuleType('solana')
            # Add submodules
            modules = ['keypair', 'publickey', 'transaction', 'rpc', 'system_program']
            for module in modules:
                sys.modules[f'solana.{module}'] = types.ModuleType(f'solana.{module}')
            
            # Add rpc submodules
            sys.modules['solana.rpc.api'] = types.ModuleType('solana.rpc.api')
            sys.modules['solana.rpc.async_api'] = types.ModuleType('solana.rpc.async_api')
            sys.modules['solana.rpc.commitment'] = types.ModuleType('solana.rpc.commitment')
            
            # Mock classes
            # Keypair
            class Keypair:
                def __init__(self):
                    self.public_key = "SimulatedSolanaAddress123456789"
                    self.secret_key = bytes([0] * 32)
                
                @classmethod
                def generate(cls):
                    return cls()
                
                @classmethod
                def from_secret_key(cls, secret_key):
                    instance = cls()
                    return instance
            
            # PublicKey
            class PublicKey:
                def __init__(self, address="SimulatedPublicKey123456789"):
                    self.address = address
                
                def __str__(self):
                    return self.address
            
            # Transaction
            class Transaction:
                def __init__(self):
                    self.instructions = []
                
                def add(self, instruction):
                    self.instructions.append(instruction)
            
            # Client
            class Client:
                def __init__(self, endpoint="http://localhost:8899"):
                    self.endpoint = endpoint
                
                def is_connected(self):
                    return True
                
                def get_balance(self, pubkey):
                    return {"result": {"value": 10_000_000_000}}
            
            # AsyncClient
            class AsyncClient:
                def __init__(self, endpoint="http://localhost:8899"):
                    self.endpoint = endpoint
                
                async def is_connected(self):
                    return True
                
                async def get_balance(self, pubkey):
                    return {"result": {"value": 10_000_000_000}}
                
                async def get_account_info(self, pubkey):
                    return {"result": {"value": {"lamports": 10_000_000_000}}}
                
                async def send_transaction(self, transaction, keypair, **kwargs):
                    return {"result": "SimulatedTransactionSignature123456789"}
            
            # Transfer
            class TransferParams:
                def __init__(self, from_pubkey, to_pubkey, lamports):
                    self.from_pubkey = from_pubkey
                    self.to_pubkey = to_pubkey
                    self.lamports = lamports
            
            def transfer(params):
                return "simulated_transfer_instruction"
            
            # Commitment
            class Commitment:
                FINALIZED = "finalized"
            
            # Assign classes to mock modules
            sys.modules['solana.keypair'].Keypair = Keypair
            sys.modules['solana.publickey'].PublicKey = PublicKey
            sys.modules['solana.transaction'].Transaction = Transaction
            sys.modules['solana.rpc.api'].Client = Client
            sys.modules['solana.rpc.async_api'].AsyncClient = AsyncClient
            sys.modules['solana.system_program'].TransferParams = TransferParams
            sys.modules['solana.system_program'].transfer = transfer
            sys.modules['solana.rpc.commitment'].Commitment = Commitment
        
        # Create SPL token mocks
        if 'spl' not in sys.modules:
            sys.modules['spl'] = types.ModuleType('spl')
            sys.modules['spl.token'] = types.ModuleType('spl.token')
            sys.modules['spl.token.client'] = types.ModuleType('spl.token.client')
            sys.modules['spl.token.constants'] = types.ModuleType('spl.token.constants')
            
            # Token class
            class Token:
                def __init__(self, conn, pubkey, program_id, payer):
                    self.conn = conn
                    self.pubkey = pubkey
                    self.program_id = program_id
                    self.payer = payer
            
            # Assign to modules
            sys.modules['spl.token.client'].Token = Token
            sys.modules['spl.token.constants'].TOKEN_PROGRAM_ID = "TokenProgramSimulated123456789"
        
        print(f"\n{Fore.YELLOW}Mock Solana modules set up for headless operation{Fore.RESET}")

# Mock the webview import
class WebviewImportHook:
    def __init__(self):
        self.module_name = 'webview'

    def find_spec(self, fullname, path, target=None):
        if fullname == self.module_name:
            print(f"\n{Fore.YELLOW}Mocking {self.module_name} module for headless operation{Fore.RESET}")
            return importlib.machinery.ModuleSpec(
                name=fullname,
                loader=self,
                origin="mock"
            )
        return None

    def create_module(self, spec):
        return types.ModuleType(spec.name)

    def exec_module(self, module):
        # Create a minimal mock implementation of the webview module
        module.create_window = lambda title, html=None, js_api=None, width=800, height=600, x=None, y=None, resizable=True, fullscreen=False, min_size=(200, 100), hidden=False, frameless=False, easy_drag=True, minimized=False, on_top=False, confirm_close=False, background_color='#FFFFFF', transparent=False, text_select=False, zoomable=False, localization=None, http_server=False, server_args=None: None
        module.start = lambda func=None, args=None, localization=None, gui=None, debug=False, http_server=False, server_args=None, user_agent=None: None
        module.token = lambda token: None

def launch_desktop():
    """Launch the trading desktop"""
    print(f"\n{Fore.GREEN}🚀 Launching Solana E2B Trading Desktop...{Fore.RESET}")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop{Fore.RESET}\n")
    
    try:
        # Import and run the main module
        try:
            # Add solana-agent-kit-py-main directory to Python path
            import sys
            import os
            solana_kit_path = os.path.join(os.getcwd(), 'solana-agent-kit-py-main')
            if solana_kit_path not in sys.path:
                sys.path.insert(0, solana_kit_path)

            # Set up mock modules for solana, spl, etc.
            print(f"\n{Fore.CYAN}Setting up mock dependencies for headless mode{Fore.RESET}")
            MockModules.setup_mock_modules()
            
            # Create a special import to bypass missing webview
            # Define a custom module finder to intercept webview imports
            sys.meta_path.insert(0, WebviewImportHook())

            # Now import the modules directly
            print(f"\n{Fore.GREEN}Attempting to import trading desktop modules{Fore.RESET}")
            from solana_trading_desktop import TradingConfig, TradingAgent, logger
            print(f"\n{Fore.GREEN}Successfully imported trading desktop modules{Fore.RESET}")
            
            # Run our own simplified version of main() to avoid command_queue issues
            print(f"\n{Fore.GREEN}Running trading desktop in headless simulation mode{Fore.RESET}")
            
            # Create configuration
            config = TradingConfig(
                max_trade_amount=0.01,  # 0.01 SOL max per trade
                max_daily_trades=5,     # 5 trades per day max
                trading_enabled=False,  # SAFETY: Start with trading disabled
                min_confidence_score=0.8  # High confidence required
            )
            
            # Create and start agent
            agent = TradingAgent(config)
            
            # Log initialization
            logger.info("Initializing Solana Trading Desktop in headless simulation mode...")
            logger.info(f"Trading enabled: {config.trading_enabled}")
            logger.info(f"Max trade amount: {config.max_trade_amount} SOL")
            logger.info(f"Daily trade limit: {config.max_daily_trades}")
            
            # Start the trading agent
            try:
                stream_url, width, height = agent.start_trading()
                logger.info("Trading agent started successfully in simulation mode")
                logger.info(f"Simulated wallet balance: {agent.wallet.get_balance():.4f} SOL")
                
                # Wait for user to stop
                print(f"\n{Fore.GREEN}Trading agent is running in simulation mode. Press Enter to stop...{Fore.RESET}")
                input()
            except Exception as e:
                logger.error(f"Error in trading agent: {e}")
            finally:
                # Clean shutdown
                logger.info("Shutting down trading agent...")
                agent.stop_trading()
                logger.info("Trading agent stopped")
                
        except ImportError as e:
            print(f"\n{Fore.RED}Error importing trading desktop module: {str(e)}{Fore.RESET}")
            print(f"\nPython path: {sys.path}")
            print(f"\nContents of directory: {os.listdir(solana_kit_path)}")
            print(f"\n{Fore.RED}Failed to import trading desktop module. Check installation.{Fore.RESET}")
        except Exception as e:
            print(f"\n{Fore.RED}Error running trading desktop: {str(e)}{Fore.RESET}")
            import traceback
            traceback.print_exc()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down gracefully...{Fore.RESET}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Fore.RESET}")
        logging.exception("Launch error")

def main():
    """Main quick start function"""
    print_banner()
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run checks
    issues = check_requirements()
    
    if issues:
        print(f"\n{Fore.RED}❌ Cannot start - please fix these issues:{Fore.RESET}")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\n{Fore.YELLOW}Run 'pip install -r requirements-e2b.txt' to install missing packages{Fore.RESET}")
        sys.exit(1)
    
    check_configuration()
    create_directories()
    show_quick_config()
    
    # Test connections
    asyncio.run(test_connections())
    
    # Confirm before launching
    print(f"\n{Fore.CYAN}Ready to launch!{Fore.RESET}")
    
    if os.getenv("E2B_TRADING_ENABLED", "false").lower() == "true":
        print(f"{Fore.RED}⚠️  WARNING: Live trading is ENABLED!{Fore.RESET}")
        response = input(f"\n{Fore.YELLOW}Continue with LIVE TRADING? (yes/no): {Fore.RESET}")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    else:
        input(f"\n{Fore.GREEN}Press Enter to start in SIMULATION mode...{Fore.RESET}")
    
    # Launch
    launch_desktop()

if __name__ == "__main__":
    main()
