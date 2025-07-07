# 📘 Complete Installation & Usage Guide

## Solana E2B Trading Desktop - Multi-Agent System

This guide will walk you through setting up and using the Solana E2B Trading Desktop, a revolutionary trading platform that combines visual desktop environments with AI-powered multi-agent consensus.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Understanding the System](#understanding-the-system)
6. [Trading Operations](#trading-operations)
7. [Safety & Risk Management](#safety--risk-management)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, or Windows with WSL2
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space
- **Internet**: Stable broadband connection

### Required Accounts

1. **E2B Account** (Free)
   - Sign up at [https://e2b.dev](https://e2b.dev)
   - Get your API key from the dashboard

2. **Solana Wallet**
   - Use existing wallet or generate new
   - Need private key in base58 format

3. **AI Provider** (at least one)
   - OpenAI: [https://platform.openai.com](https://platform.openai.com)
   - Anthropic: [https://anthropic.com](https://anthropic.com)

### Optional Services

- **Birdeye API**: Enhanced Solana data
- **Helius API**: Better RPC performance
- **Discord/Telegram**: For alerts

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/solana-e2b-trading-desktop.git
cd solana-e2b-trading-desktop

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-e2b.txt

# Copy environment template
cp .env.e2b.template .env

# Edit configuration
nano .env  # or use your favorite editor
```

### Method 2: Docker Install

```bash
# Clone repository
git clone https://github.com/yourusername/solana-e2b-trading-desktop.git
cd solana-e2b-trading-desktop

# Copy environment template
cp .env.e2b.template .env
nano .env

# Build and run
docker-compose build
docker-compose up -d
```

### Method 3: Manual Install

```bash
# Install Python packages individually
pip install e2b-desktop>=0.1.1
pip install solana-agent-kit-py>=1.0.0
pip install pywebview>=4.4.1
pip install aiohttp>=3.9.0
pip install python-dotenv>=1.0.0
pip install pandas numpy Pillow

# Clone just the scripts
mkdir solana-e2b-desktop
cd solana-e2b-desktop

# Download core files
wget https://raw.githubusercontent.com/.../solana_e2b_trading_desktop.py
wget https://raw.githubusercontent.com/.../trading_agents.py
wget https://raw.githubusercontent.com/.../browser_automation.py
# ... download other required files
```

## Configuration

### Step 1: Environment Variables

Edit your `.env` file with required values:

```env
# REQUIRED
E2B_API_KEY=e2b_... # Your E2B API key

# RECOMMENDED
OPENAI_API_KEY=sk-... # For AI analysis

# SAFETY (keep these defaults initially)
E2B_TRADING_ENABLED=false
E2B_MAX_POSITION_SIZE=0.01
```

### Step 2: Agent Configuration

Run the configuration wizard:

```bash
python e2b_desktop_config.py
```

This will:
- Check your environment
- Configure agents
- Set up directories
- Validate settings

### Step 3: Wallet Setup

If you need a new wallet:

```bash
# Generate new Solana wallet
solana-keygen new --outfile wallet.json

# Get the private key in base58 format
solana-keygen pubkey wallet.json
```

**⚠️ IMPORTANT**: Never share your private key!

## First Run

### 1. Run the Demo

See the system in action without risk:

```bash
python demo_e2b_desktop.py
```

### 2. Test Your Setup

Verify everything is configured:

```bash
python test_setup.py
```

Expected output:
```
✅ E2B API Key
✅ Solana Private Key
✅ Agent Initialization
✅ Wallet Balance: 0.1000 SOL
```

### 3. Start in Simulation Mode

```bash
python quickstart_e2b.py
```

You'll see:
- Desktop window with browser tabs
- Agent discussions in console
- Trading signals (not executed)

## Understanding the System

### The Multi-Agent Architecture

```
┌─────────────────────────────────────┐
│         Market Data Sources         │
│  DexScreener | Birdeye | Pump.fun  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│          AI Agent Council           │
├─────────────┴───────────────────────┤
│ 💼 Warren Buffett - Value Focus     │
│ 🚀 Cathie Wood - Innovation         │
│ 🛡️ Charlie Munger - Risk Check     │
│ 📊 Ben Graham - Deep Analysis       │
│ 💰 Bill Ackman - Opportunities      │
│ 🤖 Risk Manager - Safety First      │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Consensus & Execution          │
│   If confidence > 70% → Execute     │
└─────────────────────────────────────┘
```

### How Decisions Are Made

1. **Data Collection**
   - Browser automation visits sites
   - Extracts token metrics
   - Takes screenshots for analysis

2. **Agent Analysis**
   - Each agent evaluates independently
   - Different perspectives and risk levels
   - Generates confidence scores

3. **Consensus Building**
   - Weighted voting system
   - Risk Manager has veto power
   - Minimum 70% confidence required

4. **Execution**
   - Only if consensus achieved
   - Respects position limits
   - Implements stop loss/take profit

## Trading Operations

### Monitoring the System

Watch these key areas:

1. **Desktop Window**
   - Browser tabs show live data
   - Visual confirmation of analysis
   - Trade execution interface

2. **Console Output**
   ```
   [INFO] Warren Buffett: BUY signal - strong fundamentals
   [INFO] Cathie Wood: BUY signal - disruptive potential
   [INFO] Risk Manager: APPROVED - position size 2%
   [INFO] CONSENSUS: BUY BONK with 75% confidence
   ```

3. **Performance Dashboard**
   - Open browser to `http://localhost:5000`
   - Real-time metrics
   - Agent performance stats

### Manual Controls

#### Emergency Stop
```bash
# In another terminal
python emergency_stop.py panic
```

#### Pause Trading
Create a file to pause:
```bash
touch PAUSE_TRADING.flag
```

#### View Positions
```bash
cat data/active_positions.json
```

### Understanding Signals

**High Confidence (>80%)**
- Multiple agents agree
- Strong technical indicators
- Low risk assessment
- Clear opportunity

**Medium Confidence (60-80%)**
- Some disagreement
- Mixed signals
- Moderate risk
- Smaller position size

**Low Confidence (<60%)**
- No action taken
- Agents disagree
- High risk detected

## Safety & Risk Management

### Built-in Protections

1. **Position Limits**
   - Max 5% per trade (configurable)
   - Max 5 concurrent positions
   - Daily trade limit: 10

2. **Stop Loss System**
   - Automatic 5% stop loss
   - Trailing stop available
   - Emergency close all positions

3. **Agent Safeguards**
   - Risk Manager can veto any trade
   - Charlie Munger checks for dangers
   - Portfolio Manager ensures balance

### Best Practices

#### Start Small
```env
E2B_MAX_POSITION_SIZE=0.01  # 1% only
E2B_MAX_DAILY_TRADES=3      # Just 3 trades
```

#### Monitor Actively
- Keep desktop window visible
- Check logs regularly
- Set up alerts

#### Progressive Scaling
1. Week 1: Simulation only
2. Week 2: 0.01 SOL trades
3. Week 3: 0.05 SOL trades
4. Week 4: Normal parameters

### Risk Monitoring

Check risk metrics:
```bash
# View current risk status
python -c "from performance_dashboard import *; print(get_risk_report())"

# Check drawdown
grep "drawdown" logs/e2b_desktop.log
```

## Troubleshooting

### Common Issues

#### "E2B Desktop won't start"
```bash
# Check E2B API key
python -c "import os; print('E2B_API_KEY set:', bool(os.getenv('E2B_API_KEY')))"

# Test E2B connection
python -c "from e2b_desktop import Sandbox; s = Sandbox(); print('Success!')"
```

#### "No trading signals generated"
- Check market volatility (need >5% moves)
- Verify browser automation working
- Lower confidence threshold temporarily

#### "Agents always disagree"
- Normal in choppy markets
- Check agent weights in config
- Consider disabling contrarian agents

#### "High CPU/Memory usage"
```bash
# Limit concurrent operations
export E2B_MAX_ANALYSIS_THREADS=2

# Use Docker resource limits
docker-compose --file docker-compose.yml up
```

### Log Analysis

```bash
# View recent errors
grep ERROR logs/e2b_desktop.log | tail -20

# Check agent decisions
grep "CONSENSUS" logs/e2b_desktop.log

# Monitor performance
tail -f logs/e2b_desktop.log | grep -E "(TRADE|P&L|ERROR)"
```

### Recovery Procedures

#### From Emergency Stop
```bash
python emergency_stop.py recover
```

#### From Crash
```bash
# Check last state
cat data/checkpoint.json

# Resume from checkpoint
python quickstart_e2b.py --resume
```

## Advanced Usage

### Custom Agent Creation

Create your own trading personality:

```python
# my_agent.py
from trading_agents import BaseAgent, AgentPersonality, AgentRole

class MyCustomAgent(BaseAgent):
    def __init__(self, solana_kit):
        personality = AgentPersonality(
            name="My Strategy",
            role=AgentRole.CUSTOM,
            expertise=["momentum", "volume"],
            risk_tolerance=0.6,
            specialization="High volume breakouts",
            prompt_template="..."
        )
        super().__init__(personality, solana_kit)
    
    async def analyze(self, market_data):
        # Your analysis logic
        pass
```

### Custom Browser Scripts

Add new data sources:

```python
# custom_browser.py
async def analyze_custom_site(browser):
    await browser.open_url("https://custom-defi.com")
    
    # Extract custom metrics
    metrics = await browser.extract_data(
        selectors={
            "tvl": ".total-value-locked",
            "apy": ".current-apy"
        }
    )
    
    return metrics
```

### API Integration

Connect additional data sources:

```python
# In e2b_config.json
{
  "custom_apis": {
    "coingecko": {
      "enabled": true,
      "api_key": "your-key",
      "endpoints": ["simple/price", "coins/markets"]
    }
  }
}
```

### Performance Optimization

#### Faster Analysis
```python
# Parallel agent analysis
config.max_analysis_threads = 8
config.analysis_timeout = 15  # seconds
```

#### Reduce Memory Usage
```python
# Limit screenshot storage
config.browser.screenshot_retention = 100  # Keep last 100 only
config.browser.compress_screenshots = true
```

## Maintenance

### Daily Tasks
- Check performance dashboard
- Review agent accuracy
- Clear old screenshots
- Backup configuration

### Weekly Tasks
- Analyze trade history
- Adjust agent weights
- Update token watchlist
- Review risk parameters

### Monthly Tasks
- Full system backup
- Performance analysis
- Strategy refinement
- Update dependencies

## Getting Help

### Resources

- **Documentation**: `/docs` folder
- **Examples**: `demo_e2b_desktop.py`
- **Agent Details**: `trading_agents.py`
- **Configuration**: `e2b_desktop_config.py`

### Support Channels

- GitHub Issues: Bug reports
- Discord: Community chat
- Email: support@example.com

### Useful Commands

```bash
# Quick health check
python -m e2b_desktop.health_check

# Export trade history
python -m performance_dashboard export

# Generate report
python -m performance_dashboard report --period week

# Agent performance stats
python -m trading_agents stats
```

## Final Notes

Remember:
- 🚨 Start with simulation mode
- 💰 Never invest more than you can lose
- 📊 Monitor continuously
- 🛡️ Trust the risk management
- 🤖 Let agents work together
- 📈 Scale gradually

The multi-agent system is designed to be conservative by default. Trust the process, monitor carefully, and adjust parameters based on your results.

Good luck with your trading journey! 🚀
