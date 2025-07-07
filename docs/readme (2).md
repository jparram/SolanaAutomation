# SolanaAI Agent

An intelligent agent for Solana blockchain development, token trading, and NFT creation using SmolAgents and Metaplex.

## Overview

SolanaAI Agent is a comprehensive toolset that combines:

1. **SmolAgents browser automation** - for interacting with Solana websites, documentation, and block explorers
2. **On-chain transactions** - for creating, sending, and trading tokens on Solana
3. **Metaplex integration** - for NFT creation and metadata management
4. **AI assistance** - powered by various AI providers (Claude, GPT-4, local Ollama models)

This project allows developers to programmatically interact with the Solana ecosystem while leveraging AI for understanding blockchain concepts, documentation, and automating common tasks.

## Features

- 🤖 **AI-powered browser automation** for researching Solana technologies
- 💰 **Solana wallet integration** for on-chain transactions
- 🖼️ **NFT creation and minting** using Metaplex standards
- 📈 **Token information and analytics** via Birdeye API
- 📚 **Documentation extraction** from Solana and Metaplex resources
- 🔄 **Code generation** for Solana smart contracts and client code

## Installation

### Prerequisites

- Python 3.8+
- Chrome browser (for web automation)
- Node.js and npm (for TypeScript components)
- Solana CLI tools (optional but recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/solana-ai-agent.git
   cd solana-ai-agent
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install TypeScript dependencies (for Metaplex integration):
   ```bash
   cd metaplex-integration
   npm install
   cd ..
   ```

4. Set up environment variables (or create a config.json file):
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export BIRDEYE_API_KEY="your-birdeye-key"
   export OLLAMA_API_BASE="http://localhost:11434"  # if using local Ollama
   ```

## Configuration

Create a `config.json` file with your settings:

```json
{
  "default_model": "anthropic/claude-3-opus-20240229",
  "browser_model": "meta-llama/Llama-3.3-70B-Instruct",
  "dev_model": "anthropic/claude-3-opus-20240229",
  "headless_browser": false,
  "ollama_endpoint": "http://localhost:11434",
  "api_keys": {
    "openai": "your-openai-key",
    "anthropic": "your-anthropic-key",
    "xai": "your-xai-key",
    "openrouter": "your-openrouter-key",
    "birdeye": "your-birdeye-key"
  }
}
```

## Usage

### Command-Line Interface

The system provides a comprehensive CLI for all core functionality:

```bash
# Run a general query
python main.py --config config.json query "Explain how Metaplex NFTs work"

# Browse and research Solana websites
python main.py browse "Go to solscan.io and find information about the SOL token"

# Research specific documentation
python main.py explore-docs "Metaplex Token Metadata"

# Get token information
python main.py token-info "SOL"  # by symbol
python main.py token-info "So11111111111111111111111111111111111111112"  # by address

# Generate and mint an NFT
python main.py mint-nft "A futuristic Solana city with quantum computing elements"

# Analyze a website or documentation
python main.py analyze "https://docs.metaplex.com/token-metadata/getting-started"
```

### Python API

You can also use the system programmatically:

```python
from solana_chain_ai import SolanaChainAI

# Initialize the system
solana_ai = SolanaChainAI(config_path="config.json")

# Run a query
result = solana_ai.query("What is the current price of SOL?")
print(result)

# Browse the web
result = solana_ai.browse("Go to solana.com and explain the latest features")
print(result)

# Generate and mint an NFT
nft_result = solana_ai.generate_and_mint_nft("A cyberpunk Solana landscape")
print(nft_result)

# Clean up when done
solana_ai.close()
```

## Core Components

### SolanaAIAgent

The main agent that handles general queries, Solana wallet interactions, and NFT creation.

### SolanaWebBrowser

A specialized browser automation tool for navigating Solana-related websites and extracting information.

### SolanaDeveloperBrowser

An extended browser with developer-specific tools for code extraction and documentation analysis.

### MetaplexClient

TypeScript integration for Metaplex NFT operations, including creation, updates, and querying.

## Security Considerations

- **Private Keys**: Never share your configuration file with API keys or wallet private keys
- **Code Execution**: The system executes code from documentation sites - use at your own risk
- **Web Automation**: Browser automation should be monitored when performing sensitive operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
