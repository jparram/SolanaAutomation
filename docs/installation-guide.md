# SolanaAI Agent - Installation Guide

This guide provides step-by-step instructions to set up the SolanaAI Agent system for Solana blockchain development, token trading, and NFT creation.

## System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **Python**: Version 3.8 or higher
- **Node.js**: Version 16 or higher (for TypeScript components)
- **Chrome Browser**: Latest version (for web automation)
- **Disk Space**: At least 2GB free space
- **RAM**: Minimum 8GB (16GB+ recommended)
- **GPU**: Optional but recommended for local model inference

## Basic Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/solana-ai-agent.git
cd solana-ai-agent
```

### 2. Set Up Python Environment

It's recommended to use a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install all necessary packages, including:
- smolagents
- selenium
- helium
- solana
- pillow
- requests

### 4. Install TypeScript Dependencies

```bash
# Navigate to the TypeScript directory
cd metaplex-integration

# Install dependencies
npm install

# Build the TypeScript code
npm run build

# Return to the main directory
cd ..
```

### 5. Install Solana CLI Tools (Optional but Recommended)

```bash
# For macOS and Linux:
sh -c "$(curl -sSfL https://release.solana.com/v1.17.1/install)"

# For Windows:
# Download the installer from https://docs.solana.com/cli/install-solana-cli-tools
```

## Configuration

### Create Configuration File

Create a `config.json` file in the project root with your settings:

```json
{
  "default_model": "default",
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

### Set Up API Keys

You'll need to obtain API keys for the AI providers you want to use:

1. **OpenAI API Key**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **Anthropic API Key**: [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
3. **Birdeye API Key**: [https://birdeye.so/](https://birdeye.so/) (Sign up for developer access)

### Set Up Solana Wallet

You can either:

1. **Create a new wallet** (automatically done on first run)
2. **Import an existing wallet**:
   
   ```bash
   # Generate a keypair file from your private key
   echo "[1,2,3,...]" > wallet.json  # Replace with your actual private key array
   ```

## Setting Up Ollama for Local Model Inference (Optional)

For users who prefer to run models locally:

### 1. Install Ollama

Follow the instructions at [https://ollama.com/download](https://ollama.com/download) for your operating system.

### 2. Pull a Compatible Model

```bash
# Pull a Llama model (recommended)
ollama pull llama3

# Or CodeLlama for development tasks
ollama pull codellama
```

### 3. Update Configuration

Update your `config.json` to use the local model:

```json
{
  "default_model": "ollama/llama3",
  "browser_model": "ollama/llama3",
  "dev_model": "ollama/codellama",
  "ollama_endpoint": "http://localhost:11434"
}
```

## Installing the Chrome WebDriver

The browser automation requires Chrome WebDriver to function properly:

### 1. Check Your Chrome Version

Open Chrome and navigate to `chrome://version` to check your Chrome version.

### 2. Download Matching ChromeDriver

Go to [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads) and download the matching version for your system.

### 3. Add to PATH

- **Windows**: Place the `chromedriver.exe` in a directory that's in your PATH, or add its location to your PATH environment variable.
- **macOS/Linux**: Place the `chromedriver` executable in `/usr/local/bin` or another directory in your PATH.

## Verifying Installation

Run a simple test to verify everything is working correctly:

```bash
python -c "from solana_chain_ai import SolanaChainAI; agent = SolanaChainAI(); print(agent.query('What is Solana?')); agent.close()"
```

If everything is set up correctly, you should receive an informative response about Solana.

## Troubleshooting

### Common Issues and Solutions

1. **Browser automation doesn't work**:
   - Ensure Chrome and ChromeDriver versions match
   - Try running in non-headless mode (`"headless_browser": false`)

2. **API key errors**:
   - Verify API keys are correct and have sufficient permissions
   - Check for spaces or special characters in your API keys

3. **Model loading errors**:
   - Ensure you have the correct model ID
   - If using Ollama, verify the model is pulled and Ollama is running

4. **Solana transaction errors**:
   - Check your wallet has sufficient SOL for transactions
   - Verify you're connected to the correct network (mainnet, devnet, etc.)

### Getting Help

If you encounter any issues not covered in this guide:

1. Check the project issues page for similar problems
2. Consult the Solana and Metaplex documentation
3. Open a new issue with detailed information about your problem

## Next Steps

Once you've successfully installed the SolanaAI Agent, move on to the [User Guide](./USER_GUIDE.md) to learn how to use all the features.
