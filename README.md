# Solana-Automation Toolkit

**Authors**: 8bit & @0rdlibrary

This guide provides a complete walkthrough of the Solana-Automation project, a comprehensive Solana blockchain automation toolkit built in Python that enables advanced trading strategies, AI agent-based automation, DeFi protocol integrations, and secure wallet management.

## 📚 Table of Contents

### Main Project
- [Introduction](#introduction)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Core Features](#core-features)
- [Development Workflow](#development-workflow)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

### MCP Server
- [MCP Server Overview](#mcp-server-overview)
- [Server Architecture](#server-architecture)
- [API Reference](#api-reference)
- [Phala Integration](#phala-integration)
- [Deployment Guide](#deployment-guide)
- [Security Considerations](#security-considerations)
## Introduction

The Solana-Automation project is a comprehensive automation toolkit for the Solana blockchain, combining AI agent capabilities with robust trading and wallet management features. It's designed for developers and traders who need reliable, secure automation for Solana-based operations.

## Installation & Setup

### Prerequisites
- Python 3.8+ (recommended: Python 3.13+)
- Node.js 18+ and npm/pnpm
- Chrome browser (for browser automation)
- MongoDB and Redis (for data storage)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/Solana-Automation.git
cd Solana-Automation

# Create and activate a virtual environment
python -m venv solana_venv
source solana_venv/bin/activate  # On Windows: solana_venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for MCP server
cd mcp-server
npm install
cd ..

# Install Metaplex integration dependencies
cd metaplex-integration
npm install
cd ..
```

### Full Build Process

```bash
# 1. Set up Python environment
python -m venv solana_venv
source solana_venv/bin/activate

# 2. Install core Python dependencies
pip install -r requirements.txt

# 3. Install solana-agent-kit dependencies
cd solana-agent-kit-py-main
pip install -e .
cd ..

# 4. Set up MCP server
cd mcp-server
npm install
npm run build
cd ..

# 5. Set up Metaplex integration
cd metaplex-integration
npm install
npm run build
cd ..

# 6. Verify installation
python code/main-script.py --help
```
### Environment Configuration

Create a `.env` file in the project root with:

```env
# Solana Configuration
SOLANA_PRIVATE_KEY=your_private_key_here
SOLANA_RPC_URL=your_rpc_endpoint_here

# AI Provider APIs
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
XAI_API_KEY=your_xai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Third-party APIs
BIRDEYE_API_KEY=your_birdeye_key_here
PHALA_API_KEY=your_phala_key_here
HELIUS_API_KEY=your_helius_key_here

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/solana-automation
REDIS_URL=redis://localhost:6379

# Trading Configuration
TRADING_ENABLED=false
DEBUG_MODE=true
MAX_TRADE_AMOUNT=0.1
MAX_DAILY_TRADES=5

# MCP Server Configuration
BEARER_TOKEN=your_bearer_token_here
PORT=3000

# X402 Protocol Configuration
X402_ENABLED=false
X402_FACILITATOR_URL=https://facilitator.x402.com
```

## Project Structure

This project is organized into specialized directories, each serving a specific purpose in the Solana automation ecosystem:

### 📁 Core Directories

#### `/code` - Core Application Logic
- **`main-script.py`** - Main CLI interface for the SolanaChainAI system
- **`solana-ai-agent.py`** - AI agent implementation with blockchain integration
- **`solana-agent-browser-module.py`** - Browser automation for market research
- **`solana-metaplex-integration.ts`** - TypeScript integration for Metaplex NFT operations
- **`x402-integration.py`** - X402 protocol payment integration
- **`x402-umi-integration.ts`** - UMI integration for X402 protocol

#### `/config` - Configuration Management
- **`settings.py`** - Central configuration with API keys, database URIs, and environment variables
- Supports multiple AI providers (OpenAI, Anthropic, XAI, OpenRouter)
- MongoDB and Redis connection settings
- JWT authentication and Solana RPC configuration

#### `/tools` - Comprehensive Blockchain Toolkit
- **Token Operations**: `deploy_token.py`, `get_token_data.py`, `trade.py`
- **DeFi Integrations**: `use_raydium.py`, `use_drift.py`, `use_jito.py`
- **NFT Operations**: `use_metaplex.py`, `create_image.py`
- **Wallet Management**: `get_balance.py`, `transfer.py`
- **Browser Automation**: `webautomation.py`, `chromeconfig.py`

#### `/utils` - Utility Functions
- Protocol-specific utilities (Raydium, Meteora, Moonshot, Helius)
- Wallet and keypair management
- Transaction utilities and JSON conversion helpers

#### `/api` - FastAPI Web Service
- RESTful API endpoints for external integrations
- Authentication and rate limiting
- Comprehensive blockchain operation endpoints

### 📁 Specialized Modules

#### `/mcp-server` - Model Control Protocol Server
- **`src/index.ts`** - Main TypeScript server implementation
- **`package.json`** - Node.js dependencies and scripts
- **`deploy.sh`** - Cloud deployment automation
- RESTful API for Solana blockchain interactions
- Phala Network integration for confidential computing

#### `/metaplex-integration` - NFT Protocol Integration
- Metaplex standard NFT creation and minting
- Metadata management and token standards
- Integration with Solana NFT ecosystem

#### `/payment` - X402 Protocol Implementation
- **`x402_module.py`** - Payment handler with multi-token support
- Payment verification and history tracking
- HTTP client with automatic payment processing

#### `/solana-agent-kit-py-main` - Core Agent Toolkit
- **`solana_agent_kit/`** - Main package with tools and utilities
- **`tools/`** - Comprehensive Solana interaction tools
- **`examples/`** - Usage examples and integrations
- **`autogen-python/`** - AutoGen multi-agent system integration

### 📁 Data & Storage

#### `/data` - Application Data Storage
- Cache files and temporary data
- User preferences and session data

#### `/logs` - System Logging
- Application logs and debug information
- Error tracking and performance monitoring

#### `/reports` - Analytics & Reporting
- Generated reports and analytics data
- Trading performance and system metrics

#### `/screenshots` - Browser Automation Assets
- Screenshots from browser automation tasks
- Visual documentation of market research

### 📁 Additional Components

#### `/characters` - AI Agent Personalities
- Character definitions for different AI agent types
- Behavioral patterns and response templates

#### `/browser` - Web Automation
- Browser automation modules
- Market data scraping and analysis tools

#### `/tasks` - Task Management
- **`task.py`** - Task scheduling and execution system
- Automated operation management

#### `/docs` - Documentation
- **`README.md`** - Project overview and usage instructions
- **`complete_guide.md`** - Comprehensive project guide
- **`x402-*.md`** - X402 protocol documentation
- Installation guides and API references

#### `/solana_venv` - Python Virtual Environment
- Isolated Python environment with project dependencies
- Ensures consistent package versions across deployments

## Key Components
1. Trading Agent System
The core of the project is the trading agent system (
solana_trading_desktop.py
 and 
app_launcher.py
). This system:

Manages Solana wallet connections
Executes trades based on market signals
Monitors positions for stop-loss and take-profit
Provides a desktop UI for monitoring
python
# Basic usage example
from app_launcher import main

if __name__ == "__main__":
    main()
2. Wallet Management
The 
SolanaWallet
 class in 
solana_trading_desktop.py
 provides robust wallet management:

Secure key handling
Balance queries
Token operations
Transaction sending with retry logic
3. Agent System
The agent directory contains AI-powered automation agents that can:

Analyze market trends
Execute trading strategies
Monitor wallet security
Generate reports
4. Browser Integration
The browser directory provides web automation tools for:

Market data scraping
Token research
Price chart analysis
Sentiment tracking
Core Features
Automated Trading
python
# Example of setting up a trading agent
from solana_trading_desktop import TradingAgent, TradingConfig

config = TradingConfig(
    max_trade_amount=0.1,
    max_daily_trades=5,
    risk_percentage=0.02,
    trading_enabled=True
)

agent = TradingAgent(config)
agent.start_trading()
Market Analysis
The market analyzer component can:

Track token price movements
Analyze volume patterns
Monitor social sentiment
Generate trading signals
Wallet Security
The system includes multiple security features:

Private key encryption
Connection redundancy with backup RPCs
Transaction confirmation verification
Automatic session timeouts
Development Workflow
Setup Environment
Configure .env with necessary API keys
Ensure RPC endpoints are reliable
Start in Debug Mode
Set DEBUG_MODE=true in .env
Run with reduced trade amounts
Test Components
Use 
examples.py
 to test individual components
Monitor logs in the 
logs/
 directory
Deploy Trading Strategies
Create strategy in agent/strategies/
Test with paper trading
Enable live trading once validated
Best Practices
Security First
Never hardcode private keys
Use environment variables
Regularly rotate API keys
Risk Management
Set appropriate MAX_TRADE_AMOUNT
Use stop-losses consistently
Monitor the 
trading_agent.log
Performance Optimization
Use 
performance_monitor.py
 to track system health
Optimize RPC usage with connection pooling
Consider using backup RPCs during high-load periods
Troubleshooting
Common Issues:

RPC Connection Failures
Check network connectivity
Verify RPC endpoint is operational
Try alternate RPC URLs
Transaction Failures
Ensure sufficient SOL for fees
Check for network congestion
Verify transaction parameters
API Limits
Monitor rate limits on third-party APIs
Implement exponential backoff strategies
Consider premium API tiers for production
2. MCP Server Guide: Solana--Use/mcp-server
This section covers the Model Context Protocol (MCP) server integration for Solana--Use, which provides enhanced API capabilities and Phala Network integration.

📚 Table of Contents - MCP Server
MCP Server Overview
Installation & Configuration
Server Architecture
API Reference
Phala Integration
Deployment Guide
Security Considerations
MCP Server Overview
The MCP server is an Express.js-based application that extends the Solana--Use project with:

RESTful API endpoints for Solana blockchain interactions
Integration with Phala Network for confidential computing
Enhanced transaction privacy and security features
Cloud-ready deployment options
Installation & Configuration
bash
# Navigate to the MCP server directory
cd mcp-server

# Install dependencies
npm install  # or pnpm install

# Set up environment variables
cp .env.example .env
# Edit .env to add PHALA_API_KEY and other settings

# Start the server
npm start
Required Environment Variables
PHALA_API_KEY: API key for Phala Network integration
BEARER_TOKEN: Authentication token for API requests
SOLANA_RPC_URL: Solana RPC endpoint URL
PORT: Server port (default: 3000)
Server Architecture
The MCP server follows a modular architecture:

server.js: Main entry point that initializes Express and middleware
routes.js: API route definitions and handlers
phala-client.js: Client for Phala Network integration
deployment.js: Utilities for cloud deployment
javascript
// Basic usage example
const express = require('express');
const app = express();
const { setupSolanaRoutes } = require('./routes');

setupSolanaRoutes(app, solanaConnection, phalaClient);

app.listen(3000, () => {
  console.log('MCP server running on port 3000');
});
API Reference
Account Information
GET /api/account/:address

Retrieves account information with Phala-enhanced privacy.

javascript
// Example response
{
  "address": "5YNmS1R9nNSCDzb5a7mMJ1dwK9uHeAAF4CmPEwKgVWr8",
  "exists": true,
  "lamports": 100000000,
  "owner": "11111111111111111111111111111111",
  "executable": false,
  "rentEpoch": 311,
  "confidentialData": {
    "analysisTimestamp": "2025-06-13T19:47:44.000Z",
    "privacyScore": 92,
    "sensitiveOperations": false
  }
}
Token Balances
POST /api/token-balances

Retrieves multiple token balances with confidential processing.

javascript
// Request body
{
  "walletAddress": "5YNmS1R9nNSCDzb5a7mMJ1dwK9uHeAAF4CmPEwKgVWr8",
  "tokens": [
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "So11111111111111111111111111111111111111112"
  ]
}
Transaction Verification
POST /api/verify-transaction

Verifies transaction privacy using zero-knowledge proofs.

javascript
// Request body
{
  "signature": "5UfTNHekxQzUk4z7iZVp3pzDUUBwRGmH8fh7XwRrMrpDTZgf8xNv9jUVBU9FafmzZJUN6cfkQJk3wagPNNTwrAjw"
}
Network Status
GET /api/network-status

Retrieves Solana network status with Phala insights.

Phala Integration
Phala Network provides confidential computing capabilities for sensitive blockchain operations:

How It Works
Sensitive data is sent to Phala's Trusted Execution Environment
Computation happens in a secure enclave
Only verified results are returned
Zero-knowledge proofs verify integrity
Key Features
Private token balance checks
Confidential transaction analysis
Secure key management
Identity verification without revealing personal data
Deployment Guide
The MCP server can be deployed to various cloud platforms:

AWS Deployment
bash
# Configure AWS credentials
aws configure

# Set environment variables
export CLOUD_PROVIDER=aws
export CLOUD_REGION=us-east-1

# Run deployment script
node deployment.js
Google Cloud Platform
bash
# Authenticate with GCP
gcloud auth login

# Set environment variables
export CLOUD_PROVIDER=gcp
export CLOUD_PROJECT_ID=your-project-id

# Run deployment script
node deployment.js
Docker Deployment
bash
# Build Docker image
docker-compose build

# Start container
docker-compose up -d
Security Considerations
API Key Management
Store PHALA_API_KEY securely
Rotate keys regularly
Use environment variables, not hardcoded values
Authentication
Require BEARER_TOKEN for all API requests
Implement rate limiting
Consider IP whitelisting for production
Data Privacy
Use HTTPS for all connections
Leverage Phala for sensitive operations
Implement proper error handling to avoid info leaks
Monitoring
Set up logging for all API access
Monitor for unusual request patterns
Configure alerts for error conditions
This comprehensive guide should provide you with everything needed to work with both the main Solana--Use project and its MCP server component. For further details, consult the README files in each directory and the inline documentation in the code.
