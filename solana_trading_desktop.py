import os
import sys
import time
import random
import json
import asyncio
import threading
from multiprocessing import Process, Queue
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
from datetime import datetime
from pathlib import Path

# Core dependencies
from dotenv import load_dotenv
import webview
from e2b_desktop import Sandbox

# Solana dependencies
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.rpc.commitment import Commitment
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID

# Web scraping and analysis
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradingConfig:
    """Configuration for the trading agent"""
    max_trade_amount: float = 0.01  # Maximum SOL per trade
    max_daily_trades: int = 10
    risk_percentage: float = 0.02  # 2% of portfolio per trade
    stop_loss_percentage: float = 0.05  # 5% stop loss
    take_profit_percentage: float = 0.10  # 10% take profit
    min_confidence_score: float = 0.7  # Minimum confidence for trades
    trading_enabled: bool = False  # Safety switch

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    volume: float
    price_change_24h: float
    market_cap: Optional[float] = None
    timestamp: datetime = None

@dataclass
class TradeSignal:
    """Trade signal structure"""
    symbol: str
    action: str  # 'BUY' or 'SELL'
    confidence: float
    reasoning: str
    suggested_amount: float
    timestamp: datetime

class SolanaWallet:
    """Solana wallet management with robust error handling"""
    
    def __init__(self, private_key: Optional[str] = None, rpc_url: Optional[str] = None):
        # Initialize with default or provided RPC URL
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.backup_rpc_urls = [
            "https://solana-mainnet.rpc.extrnode.com", 
            "https://solana-api.projectserum.com"
        ]
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        try:
            # Parse private key safely
            if private_key:
                try:
                    secret_key = bytes(json.loads(private_key))
                except json.JSONDecodeError:
                    # Try to handle string format (base58 encoded)
                    import base58
                    secret_key = base58.b58decode(private_key)
            else:
                # Generate new keypair if none provided
                secret_key = Keypair().secret_key
                
            self.keypair = Keypair.from_secret_key(secret_key)
            
            # Initialize clients with the primary RPC URL
            self.client = Client(self.rpc_url)
            self.async_client = AsyncClient(self.rpc_url)
            
            # Test connection
            self._test_connection()
            
            logger.info(f"Wallet initialized: {self.keypair.public_key}")
            
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {e}")
            raise
            
    def _test_connection(self) -> bool:
        """Test RPC connection and fallback to backup if needed"""
        try:
            # Simple health check
            self.client.get_health()
            return True
        except Exception as e:
            logger.warning(f"Primary RPC connection failed: {e}")
            
            # Try backup RPC URLs
            for backup_url in self.backup_rpc_urls:
                try:
                    logger.info(f"Attempting connection to backup RPC: {backup_url}")
                    temp_client = Client(backup_url)
                    temp_client.get_health()
                    
                    # If successful, switch to this RPC
                    self.rpc_url = backup_url
                    self.client = Client(backup_url)
                    self.async_client = AsyncClient(backup_url)
                    logger.info(f"Switched to backup RPC: {backup_url}")
                    return True
                except Exception as backup_e:
                    logger.warning(f"Backup RPC connection failed: {backup_e}")
            
            logger.error("All RPC connections failed")
            return False
    
    def get_balance(self) -> float:
        """Get SOL balance with retry logic"""
        for attempt in range(self.max_retries):
            try:
                balance = self.client.get_balance(self.keypair.public_key)
                return balance.value / 1e9  # Convert lamports to SOL
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"Error getting balance (attempt {attempt+1}): {e}"
                    )
                    time.sleep(self.retry_delay)
                    
                    # Test connection on failure
                    if not self._test_connection():
                        logger.error("Failed to reconnect to RPC")
                else:
                    logger.error(
                        f"Failed to get balance after {self.max_retries} attempts: {e}"
                    )
                    raise
        return 0.0
    
    def get_token_balance(self, token_mint: str) -> float:
        """Get token balance with retry logic"""
        token_pubkey = PublicKey(token_mint)
        
        for attempt in range(self.max_retries):
            try:
                token = Token(
                    self.client, token_pubkey, TOKEN_PROGRAM_ID, self.keypair
                )
                account_info = token.get_accounts_by_owner(
                    self.keypair.public_key
                )
                
                if not account_info.value:
                    logger.info(f"No account found for token {token_mint}")
                    return 0.0
                    logger.warning(f"Error sending transaction (attempt {attempt+1}): {e}")
                    time.sleep(self.retry_delay)
                    
                    # Test connection on failure
                    if not self._test_connection():
                        logger.error("Failed to reconnect to RPC")
                else:
                    logger.error(f"Failed to send transaction after {self.max_retries} attempts: {e}")
        return None
        
    async def _confirm_transaction(self, signature: str) -> bool:
        """Wait for transaction confirmation"""
        try:
            commitment = Commitment("confirmed")
            await self.async_client.confirm_transaction(
                signature, 
                commitment=commitment
            )
            logger.info(f"Transaction {signature} confirmed")
            return True
        except Exception as e:
            logger.error(f"Error confirming transaction {signature}: {e}")
            return False

class MarketAnalyzer:
    """Market data analysis and signal generation"""
    
    def __init__(self):
        self.price_history: Dict[str, List[float]] = {}
        
    def fetch_market_data(self, symbols: List[str]) -> List[MarketData]:
        """Fetch market data for given symbols"""
        market_data = []
        
        for symbol in symbols:
            try:
                # Example using CoinGecko API (replace with preferred data source)
                url = f"https://api.coingecko.com/api/v3/simple/price"
                params = {
                    'ids': symbol.lower(),
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true',
                    'include_market_cap': 'true'
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if symbol.lower() in data:
                    price_data = data[symbol.lower()]
                    market_data.append(MarketData(
                        symbol=symbol,
                        price=price_data['usd'],
                        volume=0,  # Would need volume endpoint
                        price_change_24h=price_data.get('usd_24h_change', 0),
                        market_cap=price_data.get('usd_market_cap'),
                        timestamp=datetime.now()
                    ))
                    
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                
        return market_data
    
    def analyze_sentiment(self, desktop: Sandbox, search_terms: List[str]) -> Dict[str, float]:
        """Use desktop to browse and analyze market sentiment"""
        sentiment_scores = {}
        
        try:
            # Launch browser and search for market information
            desktop.launch('google-chrome')
            desktop.wait(5000)
            
            for term in search_terms:
                # Navigate to search
                desktop.press(['ctrl', 'l'])  # Address bar
                desktop.write(f"https://google.com/search?q={term} crypto news")
                desktop.press('enter')
                desktop.wait(3000)
                
                # Take screenshot for analysis
                screenshot = desktop.screenshot()
                
                # Simple sentiment analysis (in production, use proper NLP)
                sentiment_scores[term] = random.uniform(0.3, 0.9)  # Placeholder
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            
        return sentiment_scores
    
    def generate_signals(self, market_data: List[MarketData], sentiment: Dict[str, float]) -> List[TradeSignal]:
        """Generate trading signals based on market data and sentiment"""
        signals = []
        
        for data in market_data:
            # Simple signal generation logic
            confidence = 0.5
            action = 'HOLD'
            reasoning = []
            
            # Price momentum analysis
            if data.price_change_24h > 5:
                confidence += 0.2
                action = 'BUY'
                reasoning.append(f"Strong 24h gain: {data.price_change_24h:.2f}%")
            elif data.price_change_24h < -5:
                confidence += 0.2
                action = 'SELL'
                reasoning.append(f"Strong 24h loss: {data.price_change_24h:.2f}%")
            
            # Sentiment analysis
            if data.symbol.lower() in sentiment:
                sent_score = sentiment[data.symbol.lower()]
                if sent_score > 0.7:
                    confidence += 0.2
                    reasoning.append(f"Positive sentiment: {sent_score:.2f}")
                elif sent_score < 0.3:
                    confidence += 0.2
                    reasoning.append(f"Negative sentiment: {sent_score:.2f}")
            
            if action != 'HOLD' and confidence > 0.6:
                signals.append(TradeSignal(
                    symbol=data.symbol,
                    action=action,
                    confidence=confidence,
                    reasoning='; '.join(reasoning),
                    suggested_amount=0.01,  # 0.01 SOL
                    timestamp=datetime.now()
                ))
                
        return signals

class TradingAgent:
    """Main trading agent coordinator with enhanced robustness"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.state = "initializing"  # Possible states: initializing, ready, running, error, stopped
        
        # Initialize wallet with private key from environment
        try:
            private_key = os.getenv("SOLANA_PRIVATE_KEY")
            rpc_url = os.getenv("SOLANA_RPC_URL")
            self.wallet = SolanaWallet(private_key=private_key, rpc_url=rpc_url)
        except Exception as e:
            logger.critical(f"Failed to initialize wallet: {e}")
            self.state = "error"
            raise
            
        # Initialize analyzer
        self.analyzer = MarketAnalyzer()
        
        # Trading state 
        self.active_positions = {}  # Symbol -> position_data
        self.trade_count = 0
        self.daily_trade_count = 0
        self.daily_profit_loss = 0.0
        self.last_trade_reset = datetime.now()
        self.trade_history = []
        
        # Runtime control
        self.running = False
        self.desktop = None
        self.trading_thread = None
        
        # Performance monitoring
        self.start_time = None
        self.last_health_check = None
        self.error_count = 0
        self.consecutive_errors = 0
        
        # Initialize debugging framework
        self._setup_debugging()
        
        # Set state to ready
        self.state = "ready"
        logger.info("Trading agent initialized and ready")
        
    def _setup_debugging(self):
        """Setup advanced debugging and monitoring"""
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
        # Configure more detailed logging if in debug mode
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
            debug_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            for handler in logger.handlers:
                handler.setFormatter(debug_formatter)
            
            logger.debug("Debug mode enabled with enhanced logging")
            
        # Create debugging directory if it doesn't exist
        debug_dir = Path("logs/debug")
        debug_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_desktop(self):
        """Setup the desktop environment"""
        try:
            logger.info("Starting desktop sandbox...")
            self.desktop = Sandbox()
            
            width, height = self.desktop.get_screen_size()
            logger.info(f"Desktop screen size: {width}x{height}")
            
            # Start desktop stream
            self.desktop.stream.start(require_auth=True)
            auth_key = self.desktop.stream.get_auth_key()
            stream_url = self.desktop.stream.get_url(auth_key=auth_key)
            
            logger.info(f"Desktop stream URL: {stream_url}")
            
            # Launch trading interface
            self.desktop.launch('google-chrome')
            self.desktop.wait(5000)
            
            return stream_url, width, height
            
        except Exception as e:
            logger.error(f"Error setting up desktop: {e}")
            raise
    
    def check_daily_limits(self) -> bool:
        """Check if daily trading limits are reached"""
        now = datetime.now()
        if (now - self.last_trade_reset).days >= 1:
            self.trade_count = 0
            self.last_trade_reset = now
            
        return self.trade_count < self.config.max_daily_trades
    
    def calculate_position_size(self, signal: TradeSignal) -> float:
        """Calculate appropriate position size"""
        balance = self.wallet.get_balance()
        max_amount = min(
            balance * self.config.risk_percentage,
            self.config.max_trade_amount
        )
        return min(signal.suggested_amount, max_amount)
    
    async def execute_trade(self, signal: TradeSignal) -> bool:
        """Execute a trade based on signal"""
        if not self.config.trading_enabled:
            logger.info(f"Trading disabled - would execute: {signal.action} {signal.symbol}")
            return False
            
        if not self.check_daily_limits():
            logger.warning("Daily trading limit reached")
            return False
            
        if signal.confidence < self.config.min_confidence_score:
            logger.info(f"Signal confidence too low: {signal.confidence}")
            return False
            
        try:
            position_size = self.calculate_position_size(signal)
            
            logger.info(f"Executing trade: {signal.action} {position_size} SOL - {signal.symbol}")
            logger.info(f"Reasoning: {signal.reasoning}")
            
            # In a real implementation, execute the actual trade here
            # For now, we'll simulate it
            
            self.trade_count += 1
            self.active_positions[signal.symbol] = {
                'action': signal.action,
                'amount': position_size,
                'entry_price': 100.0,  # Would get actual price
                'timestamp': signal.timestamp,
                'stop_loss': 95.0,  # Calculate based on entry price
                'take_profit': 110.0  # Calculate based on entry price
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def monitor_positions(self):
        """Monitor active positions for stop loss/take profit"""
        for symbol, position in list(self.active_positions.items()):
            try:
                # Get current price (placeholder)
                current_price = 105.0  # Would get actual price
                
                # Check stop loss
                if current_price <= position['stop_loss']:
                    logger.info(f"Stop loss triggered for {symbol}")
                    # Close position
                    del self.active_positions[symbol]
                
                # Check take profit
                elif current_price >= position['take_profit']:
                    logger.info(f"Take profit triggered for {symbol}")
                    # Close position
                    del self.active_positions[symbol]
                    
            except Exception as e:
                logger.error(f"Error monitoring position {symbol}: {e}")
    
    async def trading_loop(self):
        """Main trading loop"""
        symbols = ['solana', 'bitcoin', 'ethereum']  # Add more as needed
        
        while self.running:
            try:
                logger.info("Starting trading cycle...")
                
                # Fetch market data
                market_data = self.analyzer.fetch_market_data(symbols)
                logger.info(f"Fetched data for {len(market_data)} symbols")
                
                # Analyze sentiment using desktop browsing
                if self.desktop:
                    sentiment = self.analyzer.analyze_sentiment(self.desktop, symbols)
                else:
                    sentiment = {}
                
                # Generate trading signals
                signals = self.analyzer.generate_signals(market_data, sentiment)
                logger.info(f"Generated {len(signals)} trading signals")
                
                # Execute trades
                for signal in signals:
                    await self.execute_trade(signal)
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def start_trading(self):
        """Start the trading agent"""
        self.running = True
        logger.info("Starting Solana trading agent...")
        
        # Setup desktop environment
        try:
            stream_url, width, height = self.setup_desktop()
            
            # Start trading loop in separate thread
            def run_trading_loop():
                asyncio.run(self.trading_loop())
            
            trading_thread = threading.Thread(target=run_trading_loop)
            trading_thread.daemon = True
            trading_thread.start()
            
            return stream_url, width, height
            
        except Exception as e:
            logger.error(f"Error starting trading agent: {e}")
            raise
    
    def stop_trading(self):
        """Stop the trading agent"""
        self.running = False
        logger.info("Stopping trading agent...")
        
        if self.desktop:
            self.desktop.stream.stop()
            self.desktop.kill()

def create_trading_window(stream_url: str, width: int, height: int, command_queue: Queue):
    """Create the trading desktop window"""
    window_frame_height = 29
    
    def check_queue():
        while True:
            if not command_queue.empty():
                command = command_queue.get()
                if command == 'close':
                    window.destroy()
                    break
            time.sleep(1)
    
    window = webview.create_window(
        "Solana Trading Desktop", 
        stream_url, 
        width=width, 
        height=height + window_frame_height
    )
    
    # Start queue checking thread
    t = threading.Thread(target=check_queue)
    t.daemon = True
    t.start()
    
    webview.start()

def main():
    """Main application entry point"""
    
    # Configuration
    config = TradingConfig(
        max_trade_amount=0.01,  # 0.01 SOL max per trade
        max_daily_trades=5,     # 5 trades per day max
        trading_enabled=False,  # SAFETY: Start with trading disabled
        min_confidence_score=0.8  # High confidence required
    )
    
    logger.info("Initializing Solana Trading Desktop...")
    logger.info(f"Trading enabled: {config.trading_enabled}")
    logger.info(f"Max trade amount: {config.max_trade_amount} SOL")
    logger.info(f"Daily trade limit: {config.max_daily_trades}")
    
    # Create trading agent
    agent = TradingAgent(config)
    
    try:
        # Start the trading agent
        stream_url, width, height = agent.start_trading()
        
        # Create desktop window in separate process
        command_queue = Queue()
        webview_process = Process(
            target=create_trading_window, 
            args=(stream_url, width, height, command_queue)
        )
        webview_process.start()
        
        logger.info("Trading desktop is running...")
        logger.info(f"Wallet address: {agent.wallet.keypair.public_key}")
        logger.info(f"Wallet balance: {agent.wallet.get_balance():.4f} SOL")
        
        # Keep running until user stops
        input("\nPress Enter to stop the trading agent and close the window...\n")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # Cleanup
        logger.info("Shutting down trading agent...")
        agent.stop_trading()
        
        # Close window
        command_queue.put('close')
        webview_process.join()
        
        logger.info("Trading agent stopped")

if __name__ == "__main__":
    main()
