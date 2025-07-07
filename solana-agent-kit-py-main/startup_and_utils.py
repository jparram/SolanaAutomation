# start_trading.py
#!/usr/bin/env python3
"""
Startup script for Solana Trading Desktop
Handles initialization, safety checks, and user confirmation
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import dotenv
        import solana
        import e2b_desktop
        import webview
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def load_config() -> Dict[str, Any]:
    """Load configuration from environment and config files"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Load from config.json if exists
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {
            "trading": {
                "trading_enabled": False,
                "max_trade_amount": 0.01,
                "max_daily_trades": 5
            }
        }
    
    # Override with environment variables
    config["trading"]["trading_enabled"] = os.getenv("TRADING_ENABLED", "false").lower() == "true"
    config["trading"]["max_trade_amount"] = float(os.getenv("MAX_TRADE_AMOUNT", "0.01"))
    config["trading"]["max_daily_trades"] = int(os.getenv("MAX_DAILY_TRADES", "5"))
    
    return config

def safety_check(config: Dict[str, Any]) -> bool:
    """Perform safety checks before starting"""
    issues = []
    
    # Check E2B API key
    if not os.getenv("E2B_API_KEY"):
        issues.append("❌ E2B_API_KEY not set")
    
    # Check trading settings
    if config["trading"]["trading_enabled"]:
        if config["trading"]["max_trade_amount"] > 0.1:
            issues.append("⚠️  High max trade amount (>0.1 SOL)")
        
        if config["trading"]["max_daily_trades"] > 20:
            issues.append("⚠️  High daily trade limit (>20)")
    
    # Check wallet
    if os.getenv("SOLANA_PRIVATE_KEY") and len(os.getenv("SOLANA_PRIVATE_KEY")) < 50:
        issues.append("⚠️  Private key looks too short")
    
    if issues:
        print("\n🚨 SAFETY ISSUES DETECTED:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    print("✅ Safety checks passed")
    return True

def display_startup_info(config: Dict[str, Any]):
    """Display startup information and warnings"""
    print("\n" + "="*60)
    print("🚀 SOLANA TRADING DESKTOP AGENT")
    print("="*60)
    
    print(f"\n📊 Configuration:")
    print(f"  Trading Enabled: {'🟢 YES' if config['trading']['trading_enabled'] else '🔴 NO'}")
    print(f"  Max Trade Amount: {config['trading']['max_trade_amount']} SOL")
    print(f"  Daily Trade Limit: {config['trading']['max_daily_trades']}")
    
    if config["trading"]["trading_enabled"]:
        print("\n⚠️  TRADING IS ENABLED!")
        print("   This system will make REAL trades with REAL money")
        print("   Make sure you understand the risks!")
    else:
        print("\n✅ Trading is DISABLED (simulation mode)")
        print("   The system will analyze markets but not trade")
    
    print("\n🛡️  Safety Features:")
    print("   - Stop-loss protection")
    print("   - Daily trade limits")
    print("   - Position size limits")
    print("   - Emergency stop capability")
    
    print("\n⚠️  IMPORTANT WARNINGS:")
    print("   - This is experimental software")
    print("   - Never invest more than you can afford to lose")
    print("   - Cryptocurrency trading involves significant risk")
    print("   - Monitor the system continuously")
    
    print("\n" + "="*60)

def get_user_confirmation(config: Dict[str, Any]) -> bool:
    """Get user confirmation before starting"""
    if config["trading"]["trading_enabled"]:
        print("\n🚨 REAL TRADING MODE CONFIRMATION REQUIRED")
        print("   Type 'I UNDERSTAND THE RISKS' to continue:")
        response = input("   > ")
        
        if response != "I UNDERSTAND THE RISKS":
            print("❌ Confirmation failed. Exiting for safety.")
            return False
        
        print("\n⚠️  Starting in 10 seconds. Press Ctrl+C to cancel...")
        try:
            import time
            for i in range(10, 0, -1):
                print(f"   {i}...", end=" ", flush=True)
                time.sleep(1)
            print("\n")
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return False
    else:
        print("\nPress Enter to start in simulation mode (Ctrl+C to cancel)...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return False
    
    return True

def main():
    """Main startup function"""
    print("🔍 Checking system requirements...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)
    
    # Safety checks
    if not safety_check(config):
        print("\n❌ Safety checks failed. Please review configuration.")
        sys.exit(1)
    
    # Display startup information
    display_startup_info(config)
    
    # Get user confirmation
    if not get_user_confirmation(config):
        sys.exit(0)
    
    # Start the trading agent
    print("🚀 Starting Solana Trading Desktop Agent...")
    
    try:
        # Import and start the main trading agent
        from trading_agent import main as trading_main
        trading_main()
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"\n💥 Error starting trading agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

---

# wallet_utils.py
"""
Utility functions for Solana wallet management
"""

import json
import os
from pathlib import Path
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
import logging

logger = logging.getLogger(__name__)

class WalletManager:
    """Utility class for wallet operations"""
    
    @staticmethod
    def generate_new_wallet() -> Keypair:
        """Generate a new Solana wallet"""
        keypair = Keypair()
        logger.info(f"Generated new wallet: {keypair.public_key}")
        return keypair
    
    @staticmethod
    def save_wallet(keypair: Keypair, filepath: str, password: str = None):
        """Save wallet to file (encrypted if password provided)"""
        wallet_data = {
            "public_key": str(keypair.public_key),
            "private_key": list(keypair.secret_key)
        }
        
        if password:
            # Simple encryption (in production use proper encryption)
            import base64
            data_str = json.dumps(wallet_data)
            encoded = base64.b64encode(data_str.encode()).decode()
            wallet_data = {"encrypted": encoded}
        
        with open(filepath, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        
        logger.info(f"Wallet saved to {filepath}")
    
    @staticmethod
    def load_wallet(filepath: str, password: str = None) -> Keypair:
        """Load wallet from file"""
        with open(filepath, 'r') as f:
            wallet_data = json.load(f)
        
        if "encrypted" in wallet_data:
            if not password:
                raise ValueError("Password required for encrypted wallet")
            
            import base64
            decoded = base64.b64decode(wallet_data["encrypted"]).decode()
            wallet_data = json.loads(decoded)
        
        private_key = bytes(wallet_data["private_key"])
        keypair = Keypair.from_secret_key(private_key)
        
        logger.info(f"Wallet loaded: {keypair.public_key}")
        return keypair
    
    @staticmethod
    def get_wallet_info(client: Client, public_key: PublicKey) -> dict:
        """Get comprehensive wallet information"""
        try:
            balance = client.get_balance(public_key)
            account_info = client.get_account_info(public_key)
            
            return {
                "public_key": str(public_key),
                "balance_sol": balance.value / 1e9,
                "balance_lamports": balance.value,
                "exists": account_info.value is not None,
                "executable": account_info.value.executable if account_info.value else False,
                "owner": str(account_info.value.owner) if account_info.value else None
            }
        except Exception as e:
            logger.error(f"Error getting wallet info: {e}")
            return {"error": str(e)}

def setup_wallet_interactive():
    """Interactive wallet setup"""
    print("\n🔐 Wallet Setup")
    print("="*40)
    
    wallet_file = Path("wallet.json")
    
    if wallet_file.exists():
        print("Existing wallet found.")
        choice = input("Use existing wallet? (y/n): ").lower()
        
        if choice == 'y':
            try:
                wallet = WalletManager.load_wallet(str(wallet_file))
                print(f"✅ Loaded wallet: {wallet.public_key}")
                return wallet
            except Exception as e:
                print(f"❌ Error loading wallet: {e}")
    
    print("Creating new wallet...")
    wallet = WalletManager.generate_new_wallet()
    
    save_choice = input("Save wallet to file? (y/n): ").lower()
    if save_choice == 'y':
        WalletManager.save_wallet(wallet, str(wallet_file))
    
    print(f"✅ Wallet ready: {wallet.public_key}")
    print(f"⚠️  Please save your private key securely!")
    
    return wallet

---

# monitoring.py
"""
Monitoring and alerting utilities
"""

import time
import json
import smtplib
from email.mime.text import MimeText
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor trading performance and send alerts"""
    
    def __init__(self, config: dict):
        self.config = config
        self.trades: List[Dict] = []
        self.alerts_sent = 0
        self.last_alert_time = None
        
    def record_trade(self, trade_data: Dict):
        """Record a completed trade"""
        trade_data['timestamp'] = datetime.now().isoformat()
        self.trades.append(trade_data)
        
        # Save to file
        with open('trades.json', 'w') as f:
            json.dump(self.trades, f, indent=2)
    
    def calculate_performance(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {"error": "No trades to analyze"}
        
        total_trades = len(self.trades)
        profitable_trades = sum(1 for t in self.trades if t.get('profit', 0) > 0)
        total_profit = sum(t.get('profit', 0) for t in self.trades)
        
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        # Calculate drawdown
        running_total = 0
        max_drawdown = 0
        peak = 0
        
        for trade in self.trades:
            running_total += trade.get('profit', 0)
            if running_total > peak:
                peak = running_total
            drawdown = peak - running_total
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            "total_trades": total_trades,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "average_profit": avg_profit,
            "max_drawdown": max_drawdown,
            "profitable_trades": profitable_trades,
            "losing_trades": total_trades - profitable_trades
        }
    
    def check_alerts(self) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        perf = self.calculate_performance()
        
        if "error" in perf:
            return alerts
        
        # Drawdown alert
        if perf["max_drawdown"] > self.config.get("max_drawdown_alert", 0.1):
            alerts.append(f"High drawdown detected: {perf['max_drawdown']:.2%}")
        
        # Win rate alert
        if perf["total_trades"] >= 10 and perf["win_rate"] < 0.3:
            alerts.append(f"Low win rate: {perf['win_rate']:.2%}")
        
        # Daily loss alert
        today_trades = [t for t in self.trades 
                       if datetime.fromisoformat(t['timestamp']).date() == datetime.now().date()]
        today_profit = sum(t.get('profit', 0) for t in today_trades)
        
        if today_profit < -self.config.get("daily_loss_limit", 0.05):
            alerts.append(f"Daily loss limit exceeded: {today_profit:.4f} SOL")
        
        return alerts
    
    def send_alert(self, message: str):
        """Send alert notification"""
        # Rate limiting
        if self.last_alert_time and (datetime.now() - self.last_alert_time) < timedelta(minutes=30):
            return
        
        logger.warning(f"ALERT: {message}")
        
        # Email alert (if configured)
        email_config = self.config.get("email_alerts", {})
        if email_config.get("enabled", False):
            try:
                self._send_email_alert(message, email_config)
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        self.last_alert_time = datetime.now()
        self.alerts_sent += 1
    
    def _send_email_alert(self, message: str, email_config: dict):
        """Send email alert"""
        msg = MimeText(f"Trading Alert: {message}")
        msg['Subject'] = "Solana Trading Agent Alert"
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            if email_config.get('use_tls', True):
                server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
    
    def generate_report(self) -> str:
        """Generate performance report"""
        perf = self.calculate_performance()
        
        if "error" in perf:
            return "No trading data available"
        
        report = f"""
🤖 Solana Trading Agent Performance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Overall Statistics:
  Total Trades: {perf['total_trades']}
  Win Rate: {perf['win_rate']:.2%}
  Total Profit: {perf['total_profit']:.6f} SOL
  Average Profit: {perf['average_profit']:.6f} SOL
  Max Drawdown: {perf['max_drawdown']:.6f} SOL

💰 Trade Breakdown:
  Profitable: {perf['profitable_trades']}
  Losing: {perf['losing_trades']}
  
🚨 Alerts Sent: {self.alerts_sent}
        """
        
        return report.strip()

def setup_monitoring():
    """Setup monitoring configuration"""
    config = {
        "max_drawdown_alert": 0.1,  # 10% drawdown
        "daily_loss_limit": 0.05,   # 0.05 SOL daily loss
        "email_alerts": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "use_tls": True,
            "from": "your-email@gmail.com",
            "to": "alerts@yourdomain.com",
            "username": "your-email@gmail.com",
            "password": "your-app-password"
        }
    }
    
    return PerformanceMonitor(config)

---

# emergency_stop.py
"""
Emergency stop functionality
"""

import signal
import sys
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmergencyStop:
    """Emergency stop handler"""
    
    def __init__(self, trading_agent):
        self.trading_agent = trading_agent
        self.stop_file = "emergency_stop.json"
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        """Handle emergency stop signal"""
        logger.critical(f"Emergency stop triggered by signal {signum}")
        self.execute_emergency_stop("Signal received")
    
    def execute_emergency_stop(self, reason: str):
        """Execute emergency stop procedure"""
        timestamp = datetime.now().isoformat()
        
        logger.critical(f"EMERGENCY STOP: {reason}")
        
        # Stop trading immediately
        if hasattr(self.trading_agent, 'config'):
            self.trading_agent.config.trading_enabled = False
        
        # Record emergency stop
        stop_data = {
            "timestamp": timestamp,
            "reason": reason,
            "active_positions": getattr(self.trading_agent, 'active_positions', {}),
            "trade_count": getattr(self.trading_agent, 'trade_count', 0)
        }
        
        with open(self.stop_file, 'w') as f:
            json.dump(stop_data, f, indent=2)
        
        # Try to close positions safely
        self._close_all_positions()
        
        logger.critical("Emergency stop completed")
        sys.exit(0)
    
    def _close_all_positions(self):
        """Attempt to close all active positions"""
        try:
            if hasattr(self.trading_agent, 'active_positions'):
                for symbol, position in self.trading_agent.active_positions.items():
                    logger.warning(f"Emergency closing position: {symbol}")
                    # Implementation would depend on exchange API
        except Exception as e:
            logger.error(f"Error closing positions during emergency stop: {e}")
    
    def check_stop_file(self) -> bool:
        """Check if emergency stop file exists"""
        try:
            with open(self.stop_file, 'r') as f:
                stop_data = json.load(f)
            
            logger.warning(f"Emergency stop file found from {stop_data['timestamp']}")
            logger.warning(f"Reason: {stop_data['reason']}")
            
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error reading emergency stop file: {e}")
            return False
    
    def clear_stop_file(self):
        """Clear emergency stop file after review"""
        try:
            import os
            if os.path.exists(self.stop_file):
                os.remove(self.stop_file)
                logger.info("Emergency stop file cleared")
        except Exception as e:
            logger.error(f"Error clearing emergency stop file: {e}")
