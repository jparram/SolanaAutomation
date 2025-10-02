# Solana-Automation Toolkit

[![CI](https://github.com/jparram/SolanaAutomation/workflows/CI/badge.svg)](https://github.com/jparram/SolanaAutomation/actions/workflows/ci.yml)
[![Python CI](https://github.com/jparram/SolanaAutomation/workflows/Python%20CI/badge.svg)](https://github.com/jparram/SolanaAutomation/actions/workflows/python-ci.yml)
[![TypeScript CI](https://github.com/jparram/SolanaAutomation/workflows/TypeScript%20CI/badge.svg)](https://github.com/jparram/SolanaAutomation/actions/workflows/typescript-ci.yml)
[![CodeQL](https://github.com/jparram/SolanaAutomation/workflows/CodeQL%20Security%20Analysis/badge.svg)](https://github.com/jparram/SolanaAutomation/actions/workflows/codeql-analysis.yml)
[![OSSF Scorecard](https://github.com/jparram/SolanaAutomation/workflows/OSSF%20Scorecard/badge.svg)](https://github.com/jparram/SolanaAutomation/actions/workflows/scorecard.yml)

```
   ███████╗ ██████╗ ██╗      █████╗ ███╗   ██╗ █████╗ 
   ██╔════╝██╔═══██╗██║     ██╔══██╗████╗  ██║██╔══██╗
   ███████╗██║   ██║██║     ███████║██╔██╗ ██║███████║
   ╚════██║██║   ██║██║     ██╔══██║██║╚██╗██║██╔══██║
   ███████║╚██████╔╝███████╗██║  ██║██║ ╚████║██║  ██║
   ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                                                       
    █████╗ ██╗    ██╗████████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
   ██╔══██╗██║    ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
   ███████║██║    ██║   ██║   ██║   ██║██╔████╔██║███████║   ██║   ██║██║   ██║██╔██╗ ██║
   ██╔══██║██║    ██║   ██║   ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
   ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
   ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

**Authors**: 8bit & @0rdlibrary

## 🚀 Introduction: The Solana Terminals AI Automation Platform

This guide outlines a comprehensive, multi-agent platform designed for sophisticated interaction with the Solana ecosystem. It combines a user-friendly desktop interface with powerful backend services for AI-driven research, browser automation, and automated trading.

At its core, the system functions as a **Multi-Agent Consensus Platform (MCP)**, where specialized AI agents collaborate to analyze data, propose actions, and execute trades. The entire process is orchestrated by a central **Terminagent**, which acts as the conductor, coordinating the actions of the agent council and ensuring a cohesive strategy.

### 🎯 Key Capabilities

```
🤖 Automated Research      🧠 Intelligent Trading      🔗 On-Chain Interaction
Deploy AI agents to        Utilize a council of AI     Seamlessly execute 
autonomously browse        personas, each with a       transactions, manage
websites, read docs,       unique investment           assets, and mint NFTs
and extract critical       philosophy, to build        through integrated
information about         consensus on trading        wallet and Metaplex
Solana projects.          decisions.                  functionalities.

💰 Internet-Native Payments
Process micropayments for premium data or services using the innovative 
x402 protocol, allowing agents to operate as autonomous economic entities.
```

## 📚 Table of Contents

### Main Project
- [🏗️ System Architecture](#system-architecture)
- [⚙️ Installation & Setup](#installation--setup)
- [📁 Project Structure](#project-structure)
- [🔧 Core Components](#core-components)
- [🎨 Frontend - Trading Desktop](#frontend---solana-e2b-trading-desktop)
- [🔐 Security & Best Practices](#security--best-practices)
- [🚀 Deployment Guide](#deployment-guide)
- [🔄 CI/CD & Security Scanning](#cicd--security-scanning)

### MCP Server
- [🌐 MCP Server Overview](#mcp-server-overview)
- [🏭 Server Architecture](#server-architecture)
- [📡 API Reference](#api-reference)
- [🔒 Phala Integration](#phala-integration)
- [💳 X402 Payment Protocol](#x402-payment-protocol)

---

## 🏗️ System Architecture

The platform is built on a modern microservices architecture, ensuring scalability and maintainability:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           🖥️  CLIENT LAYER                                         │
│                    Solana E2B Trading Desktop (React)                              │
│            Wallet connectivity • Real-time dashboards • Manual controls           │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            🌐 API LAYER                                            │
│                         MCP Server (FastAPI)                                       │
│                   RESTful APIs • WebSocket connections                             │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        🤖 SERVICE LAYER                                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  Terminagent    │  │ Browser Service │  │Blockchain Service│  │ Payment Service ││
│  │  (Orchestrator) │  │ Web Automation  │  │ On-chain Ops    │  │ x402 Protocol   ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘│
│                                                                                     │
│                        🧠 AI Agent Council                                         │
│     Warren Buffett • Cathie Wood • Charlie Munger • Ben Graham • Risk Manager     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           💾 DATA LAYER                                            │
│                MongoDB (Persistent) • Redis (Cache & Messaging)                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## ⚙️ Installation & Setup

### 📋 Prerequisites

```bash
# System Requirements
OS: Linux, macOS, or Windows with WSL2
Python: 3.8+ (recommended: 3.13+)
Node.js: 16+ and npm/pnpm
RAM: 16GB recommended
Chrome browser (for browser automation)
```

### 🔑 Required Accounts

- **E2B Account**: For sandboxed cloud browser environments ([Get API key](https://e2b.dev))
- **AI Provider Keys**: OpenAI, Anthropic, or other supported models
- **Solana Wallet**: A base58 private key for on-chain actions
- **MongoDB & Redis**: For data storage (local or cloud)

### 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Solana-Automation.git
cd Solana-Automation

# 2. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit the .env file with your API keys

# 3. Frontend Setup
cd ../frontend
npm install
cp .env.example .env
# Edit the .env file to point to the backend API URL

# 4. Install additional dependencies
cd ../mcp-server
npm install
cd ../metaplex-integration
npm install
```

### 🐳 Docker Setup (Recommended)

```bash
# Ensure Docker and Docker Compose are installed
docker-compose build
docker-compose up -d
```

This will launch the backend server, React frontend, MongoDB, and Redis containers.

### 🌍 Environment Configuration

Create `.env` files in the appropriate directories with:

```env
# Solana Configuration
SOLANA_PRIVATE_KEY=your_private_key_here
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_HELIUS_API_KEY

# AI Provider APIs
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
XAI_API_KEY=your_xai_api_key_here

# Third-party APIs
HELIUS_API_KEY=your_helius_api_key_here
E2B_API_KEY=your_e2b_api_key_here
PHALA_API_KEY=your_phala_api_key_here

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/solana-automation
REDIS_URL=redis://localhost:6379

# Trading Configuration
TRADING_ENABLED=false
DEBUG_MODE=true
MAX_TRADE_AMOUNT=0.1
MAX_DAILY_TRADES=5
```

## 📁 Project Structure

```
Solana-Automation/
├── 📁 code/                    # Core application logic
│   ├── main-script.py          # Main CLI interface
│   ├── solana-ai-agent.py      # AI agent implementation
│   └── x402-integration.py     # Payment protocol integration
├── 📁 mcp-server/              # Model Control Protocol server
│   ├── src/index.ts            # TypeScript server implementation
│   └── package.json            # Node.js dependencies
├── 📁 tools/                   # Blockchain toolkit
│   ├── deploy_token.py         # Token deployment
│   ├── use_raydium.py          # DeFi integrations
│   └── get_balance.py          # Wallet operations
├── 📁 payment/                 # X402 protocol implementation
├── 📁 metaplex-integration/    # NFT protocol integration
├── 📁 api/                     # FastAPI web service
├── 📁 characters/              # AI agent personalities
├── 📁 browser/                 # Web automation modules
├── 📁 utils/                   # Utility functions
├── 📁 config/                  # Configuration management
├── 📁 data/                    # Application data storage
├── 📁 logs/                    # System logging
└── 📁 docs/                    # Documentation
```

## 🔧 Core Components

### 🤖 The Terminagent & Agent Council

When a user initiates a task, such as *"Research the BONK token and decide if it's a good investment"*, the Terminagent coordinates the following workflow:

```
1. 📊 Data Collection
   └── Browser agent visits sites (Birdeye, DexScreener, official websites)
   └── Extracts key metrics, tokenomics, community sentiment
   └── Takes screenshots for visual analysis

2. 🧠 Independent Analysis
   └── Warren Buffett:  Focuses on fundamentals & long-term value
   └── Cathie Wood:     Looks for disruptive innovation potential
   └── Charlie Munger:  Acts as risk checker, identifies red flags
   └── Ben Graham:      Performs deep value analysis
   └── Risk Manager:    Assesses overall risk, has ultimate veto power

3. 🗳️ Consensus Building
   └── Agents "vote" on action (BUY/SELL/HOLD)
   └── Provides confidence scores
   └── Trade executed only if weighted confidence > 70%

4. ⚡ Execution
   └── If consensus reached and Risk Manager approves
   └── Blockchain Service executes trade
   └── Respects all safety parameters
```

### 🌐 API Endpoints

The FastAPI server exposes modular endpoints:

- **`/api/auth/`** - User registration, login, profile management
- **`/api/agent/`** - Terminagent task initiation and monitoring
- **`/api/browser/`** - Direct browser automation control
- **`/api/blockchain/`** - On-chain data and transaction endpoints
- **`/api/payment/`** - X402 payment management and tracking

## 🎨 Frontend - Solana E2B Trading Desktop

The React frontend provides a comprehensive interface for monitoring and controlling the multi-agent system:

### 🖥️ Key Components

```
📊 Dashboard                    💬 Agent Chat Interface
├── Active positions            ├── Conversational UI
├── P&L tracking               ├── Command issuance
├── Agent performance          ├── Real-time thought process
└── Market metrics             └── Task monitoring

🌐 Browser Automation View     🔧 Manual Controls
├── Live browser view          ├── 🛑 Emergency Stop
├── Screenshots & logs         ├── ⏸️ Pause Trading
├── Automation status          └── 📊 Position Management
└── Data extraction results
```

### 🔐 Wallet Integration

- Connects via Solana Wallet Adapter
- Authentication and manual transaction signing
- Real-time balance monitoring
- Multi-wallet support

## 💳 X402 Payment Protocol - Enabling Autonomous Agents

The platform integrates the **x402 payment protocol** to allow agents to autonomously access paid APIs or premium data:

### 🔄 How It Works

```
1. Agent makes HTTP request to premium resource
2. Server responds with 402 Payment Required
3. X402PaymentHandler automatically detects payment requirement
4. Constructs, signs, and sends required SPL token payment
5. Upon successful payment, original request is retried
6. Agent gains access to premium data
```

### 💰 Autonomous Economy

- AI agents function as true autonomous economic entities
- Automatically pays for high-resolution market data when needed
- Configurable `auto_approve_threshold` prevents uncontrolled spending
- Manual approval required for payments above threshold

## 🔐 Security & Best Practices

### 🛡️ Security Measures

```
✅ Environment Variables Only    ✅ Private Key Encryption
✅ API Key Rotation             ✅ Connection Redundancy
✅ Transaction Confirmation     ✅ Automatic Session Timeouts
✅ Rate Limiting               ✅ Input Validation
```

### ⚠️ Important Security Notes

1. **Never commit sensitive data** - All API keys are in `.env` files (gitignored)
2. **Use placeholder values** - All examples use `your_api_key_here`
3. **Rotate keys regularly** - Set up automated key rotation
4. **Monitor spending** - Configure trading limits and alerts
5. **Test in sandbox** - Always test with minimal amounts first

### 🔄 Risk Management

- Set appropriate `MAX_TRADE_AMOUNT`
- Use stop-losses consistently
- Monitor `trading_agent.log` for issues
- Implement emergency stop functionality
- Configure backup RPC endpoints

## 🚀 Deployment Guide

### 🐳 Containerization

The entire application is containerized using Docker:

```bash
# Build and deploy
docker-compose build
docker-compose up -d

# Monitor logs
docker-compose logs -f
```

### ☁️ Cloud Deployment

#### AWS Deployment
```bash
# Configure AWS credentials
aws configure

# Set environment variables
export CLOUD_PROVIDER=aws
export CLOUD_REGION=us-east-1

# Deploy
node deployment.js
```

#### Google Cloud Platform
```bash
# Authenticate with GCP
gcloud auth login

# Set environment variables
export CLOUD_PROVIDER=gcp
export CLOUD_PROJECT_ID=your-project-id

# Deploy
node deployment.js
```

### 📊 Monitoring & Maintenance

- **Logging**: All API access and agent actions logged
- **Alerts**: Configure alerts for error conditions
- **Performance**: Monitor resource usage and response times
- **Backups**: Regular database backups
- **Updates**: CI/CD pipeline for automated deployments

## 🌟 Getting Started

1. **Set up your environment** following the installation guide
2. **Configure your API keys** in the `.env` files
3. **Start with debug mode** and minimal trade amounts
4. **Test individual components** using the examples
5. **Deploy trading strategies** after thorough testing
6. **Monitor and optimize** using the performance tools

## 🔄 CI/CD & Security Scanning

This project includes comprehensive CI/CD pipelines with automated security scanning:

### Automated Workflows

- **🔍 Python CI** - Linting (ruff, black, isort), type checking (mypy), security scanning (pip-audit), and testing (pytest)
- **🔧 TypeScript CI** - Build verification, linting (ESLint), formatting (Prettier), and security scanning (npm audit)
- **🛡️ CodeQL Analysis** - Advanced security vulnerability detection for Python and JavaScript/TypeScript
- **📊 OSSF Scorecard** - Repository security posture assessment with 18+ security checks
- **🤖 Dependabot** - Automated dependency updates for Python, npm, and GitHub Actions

### Security Features

All workflows include:
- Dependency vulnerability scanning
- Static code analysis
- Best practice enforcement
- Weekly security audits
- Automated security updates via Dependabot

### Documentation

For detailed information about the CI/CD setup, configuration, and local usage, see [CI_CD_SETUP.md](CI_CD_SETUP.md).

### Running Checks Locally

**Python:**
```bash
# Install tools
pip install ruff black isort mypy pytest pip-audit

# Run checks
ruff check .
black --check .
isort --check-only .
mypy .
pip-audit
pytest
```

**TypeScript:**
```bash
cd mcp-server
npm install
npm run lint
npm run format:check
npm run build
npm audit
```

## 🤝 Contributing

This project is developed by **8bit** and **@0rdlibrary**. Contributions are welcome!

All contributions are automatically checked by our CI/CD pipelines. Please ensure your code passes linting, formatting, and security checks before submitting a PR.

## 📄 License

This project is licensed under the MIT License.

---

*The Solana Terminals AI Automation platform represents a significant leap forward in applying AI to the blockchain space. By combining a multi-agent consensus mechanism with powerful browser automation, direct blockchain integration, and autonomous payment capabilities, it provides a sophisticated and highly extensible framework for developers and traders seeking to automate their strategies and gain a deeper, AI-driven understanding of the Solana ecosystem.*