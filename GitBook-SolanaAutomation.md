# Solana Automation & Browser Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Installation & Setup](#installation--setup)
4. [Solana Web Browser Module](#solana-web-browser-module)
   - [Core Features](#core-features)
   - [Implementation Details](#implementation-details)
   - [Usage Examples](#usage-examples)
5. [MCP Server Integration](#mcp-server-integration)
   - [Server Architecture](#server-architecture)
   - [Phala Integration](#phala-integration)
   - [API Endpoints](#api-endpoints)
6. [Deployment Options](#deployment-options)
7. [Testing & Debugging](#testing--debugging)
8. [Security Best Practices](#security-best-practices)
9. [Advanced Usage](#advanced-usage)
10. [Troubleshooting](#troubleshooting)

## Introduction

The Solana Automation project is a comprehensive toolkit designed to automate interactions with the Solana blockchain. It provides tools for:

- Browser-based automation for interacting with Solana websites
- Confidential computing integration via Phala Network
- API endpoints for secure Solana data access
- Trading automation capabilities

This guide covers the installation, configuration, and usage of the entire system with a focus on the browser automation module and MCP server integration.

## Project Structure

The project is organized into several key components:

```
SolanaAutomation/
├── Solana--Use/            # Main Python project
│   ├── browser/            # Browser automation module
│   │   ├── solana_web_browser.py
│   │   ├── test_browser.py
│   │   └── screenshots/    # Browser screenshots
│   ├── agents/             # Trading and automation agents
│   ├── config/             # Configuration files
│   ├── utils/              # Utility functions
│   ├── solana_trading_desktop.py  # Core trading logic
│   ├── app_launcher.py     # Entry point
│   └── solana_venv/        # Python virtual environment
│
└── mcp-server/            # MCP server components
    └── solana-mcp/         # Solana-specific MCP server
        ├── server.js       # Express server setup
        ├── routes.js       # API endpoints
        ├── phala-client.js # Phala integration
        ├── deployment.js   # Deployment script
        └── package.json    # Dependencies
```

## Installation & Setup

### Prerequisites

- Node.js 16+ for MCP server
- Python 3.9+ for main project
- Chrome or Chromium browser for web automation
- ChromeDriver matching your Chrome version

### Setting Up the Python Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SolanaAutomation/Solana--Use
   ```

2. Activate the virtual environment:
   ```bash
   source solana_venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install selenium solana-py web3
   ```

### Setting Up the MCP Server

1. Navigate to the MCP server directory:
   ```bash
   cd ../mcp-server/solana-mcp
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment configuration:
   ```bash
   cp .env.example .env
   # Edit the .env file with your specific configuration
   ```

## Solana Web Browser Module

The Solana Web Browser module is a powerful automation tool built on Selenium that allows programmatic interaction with Solana-related websites.

### Core Features

- **Headless Operation**: Run automated browser sessions without a visible UI
- **Screenshot Capability**: Capture webpage states for verification or reporting
- **Solana Explorer Integration**: Automatically check address information
- **Token Price Checks**: Fetch token price data from sources like Birdeye
- **Natural Language Instructions**: Interpret simple text commands

### Implementation Details

The module is implemented in `solana_web_browser.py` with the following key components:

1. **SolanaWebBrowser Class**: Main class that handles browser initialization and control
   ```python
   class SolanaWebBrowser:
       def __init__(self, headless: Optional[bool] = None, model_id: Optional[str] = None):
           self.headless = headless if headless is not None else False
           self.model_id = model_id or "default"
           # Browser initialization
   ```

2. **Core Browser Utilities**:
   - Browser initialization with configurable options
   - Navigation to URLs
   - Element interaction (click, input)
   - Screenshot capture
   - Error handling and recovery

3. **Specialized Solana Functions**:
   - Checking address information on Solana Explorer
   - Looking up token prices on platforms like Birdeye
   - Parsing and executing natural language instructions

### Usage Examples

**Basic Initialization**:
```python
from browser.solana_web_browser import SolanaWebBrowser

# Initialize browser (visible mode)
browser = SolanaWebBrowser(headless=False)

# Always close when done
try:
    # Your operations here
    pass
finally:
    browser.close()
```

**Checking a Solana Address**:
```python
# Check information about a wallet address
address_info = browser.check_solana_explorer("4Zw5RukqrwJMV3FVaHJgPXz7HEyGbhJq4L9L9YpmMhRW")
print(f"SOL Balance: {address_info.get('sol_balance')}")
print(f"Token Count: {address_info.get('token_count')}")
```

**Looking Up Token Prices**:
```python
# Check token price information
token_info = browser.check_token_price("SOL")
print(f"Current Price: ${token_info.get('price')}")
print(f"24h Change: {token_info.get('change_24h')}%")
```

**Using Natural Language Instructions**:
```python
# Execute a task using natural language
result = browser.run("navigate to raydium.io and take a screenshot")
print(f"Task completed, screenshot saved to: {result.get('screenshot')}")
```

**Testing Script Usage**:
```bash
# Test specific functionality (explorer, token, navigate, all)
python browser/test_browser.py --task explorer --address YOUR_ADDRESS
python browser/test_browser.py --task token --token SOL
python browser/test_browser.py --task all --headless
```

## MCP Server Integration

The Model Context Protocol (MCP) server provides a secure API layer for interacting with Solana data, enhanced with confidential computing capabilities through Phala Network.

### Server Architecture

The server is built on Express.js with a modular structure:

- `server.js`: Core server initialization and configuration
- `routes.js`: API endpoint definitions
- `phala-client.js`: Phala Network integration for confidential computing

### Phala Integration

The integration with Phala Network adds confidential computing capabilities:

```javascript
// phala-client.js
const createPhalaClient = (apiKey) => {
  return {
    // Confidential computation methods
    computeConfidential: async (data) => {
      // Implementation details
    },
    verifyZkProof: async (proof, publicInputs) => {
      // Implementation details
    }
  };
};
```

### API Endpoints

The server exposes several endpoints for Solana interaction:

1. **Account Information**:
   ```
   GET /api/account/:address
   ```
   Fetches account information with privacy enhancement.

2. **Token Balances**:
   ```
   GET /api/tokens/:owner
   ```
   Retrieves token balances with confidential computation.

3. **Transaction Privacy**:
   ```
   POST /api/verify-privacy
   ```
   Verifies transaction privacy using zero-knowledge proofs.

4. **Health Check**:
   ```
   GET /health
   ```
   Returns server and API status information.

## Deployment Options

The project includes a `deployment.js` script that supports multiple cloud providers:

### AWS Deployment

```javascript
// Example AWS deployment configuration
const awsConfig = {
  region: 'us-east-1',
  instanceType: 't3.medium',
  // Other AWS-specific configuration
};

deployToAWS(awsConfig);
```

### GCP Deployment

```javascript
// Example GCP deployment configuration
const gcpConfig = {
  project: 'solana-automation',
  region: 'us-central1',
  // Other GCP-specific configuration
};

deployToGCP(gcpConfig);
```

### Azure Deployment

```javascript
// Example Azure deployment configuration
const azureConfig = {
  resourceGroup: 'solana-resources',
  region: 'eastus',
  // Other Azure-specific configuration
};

deployToAzure(azureConfig);
```

## Testing & Debugging

### Browser Module Testing

The project includes a dedicated test script `test_browser.py`:

```python
# Run tests with different configurations
python browser/test_browser.py --task all
python browser/test_browser.py --task explorer --headless
python browser/test_browser.py --task navigate --address YOUR_ADDRESS
```

### MCP Server Testing

Test API endpoints using curl or Postman:

```bash
# Test health endpoint
curl http://localhost:3000/health

# Test account endpoint (replace with valid address)
curl http://localhost:3000/api/account/4Zw5RukqrwJMV3FVaHJgPXz7HEyGbhJq4L9L9YpmMhRW
```

### Debugging Tips

1. **Browser Automation Debugging**:
   - Set `headless=False` to see browser actions in real-time
   - Check screenshot captures for visual debugging
   - Review browser logs for JavaScript errors

2. **MCP Server Debugging**:
   - Use logging with various levels (info, debug, error)
   - Monitor server stdout/stderr for issues
   - Implement proper error handling with detailed messages

## Security Best Practices

### API Key Security

1. **Environment Variables**: Store sensitive API keys and tokens in environment variables, never hardcoded.
   ```bash
   # .env file example
   PHALA_API_KEY=your_api_key_here
   SOLANA_RPC_URL=https://your-rpc-url
   BEARER_TOKEN=your_secure_token
   ```

2. **Access Control**: Implement proper authentication and rate limiting on API endpoints.
   ```javascript
   // Example middleware for bearer token auth
   const authenticate = (req, res, next) => {
     const token = req.headers.authorization?.split('Bearer ')[1];
     if (token !== process.env.BEARER_TOKEN) {
       return res.status(401).json({ error: 'Unauthorized' });
     }
     next();
   };
   ```

### Private Key Protection

1. Never store private keys directly in code or unencrypted files
2. Use HSM or secure key management services when possible
3. Implement proper access control for local key storage

## Advanced Usage

### Integration with Trading Agents

```python
from browser.solana_web_browser import SolanaWebBrowser
from agents.trading_agent import TradingAgent

# Initialize components
browser = SolanaWebBrowser(headless=True)
agent = TradingAgent(config={
    'strategy': 'momentum',
    'risk_level': 'medium'
})

# Integrate browser data with trading agent
token_data = browser.check_token_price('SOL')
decision = agent.evaluate_trade(token_data)

if decision['action'] == 'buy':
    # Execute buy operation
    pass
```

### Custom Automation Scripts

Create custom automation scripts for specific tasks:

```python
def monitor_token_launch(browser, token_symbol, target_price, duration_hours):
    """
    Monitor a token launch and execute actions when price reaches target
    """
    end_time = time.time() + (duration_hours * 3600)
    
    while time.time() < end_time:
        try:
            token_data = browser.check_token_price(token_symbol)
            current_price = float(token_data.get('price', 0))
            
            if current_price >= target_price:
                # Execute target price action
                return {'success': True, 'trigger_price': current_price}
                
            # Wait before checking again
            time.sleep(300)  # 5 minutes
            
        except Exception as e:
            logger.error(f"Error monitoring token: {str(e)}")
            time.sleep(60)  # Wait a minute on error
            
    return {'success': False, 'timeout': True}
```

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| **ChromeDriver version mismatch** | Update ChromeDriver to match your Chrome version |
| **Selenium element not found** | Increase wait times or use more robust selectors |
| **MCP server connection refused** | Check if server is running and port is correct |
| **API authentication errors** | Verify environment variables and token configuration |
| **Phala API errors** | Check Phala API key and network status |

### Browser Module Issues

- **Element interaction failures**: The page structure may have changed. Update selectors in the code.
- **Headless mode issues**: Try with `headless=False` to see what's happening visually.
- **Performance problems**: Adjust wait times or implement connection pooling.

### MCP Server Issues

- **Memory leaks**: Implement proper request cleanup and monitor memory usage.
- **Slow response times**: Add caching for frequently requested data.
- **Connection timeouts**: Set appropriate timeout values for external API calls.

---

This guide covers the core components of the Solana Automation project. For specific implementation details, refer to the source code and comments within each file.

© 2025 Solana Automation Project
