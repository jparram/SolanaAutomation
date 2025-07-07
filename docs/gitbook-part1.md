# Part 1: Setting Up Your Development Environment

Before we start building our SolanaAI Agent platform, we need to set up a proper development environment with all the necessary tools and dependencies.

## Installing Required Software

First, let's install all the software required for development:

### 1. Python Setup

We'll be using Python 3.9+ for our backend. Install it from [python.org](https://python.org) or use a package manager:

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip

# For macOS using Homebrew
brew install python@3.9

# For Windows, download the installer from python.org
```

Verify the installation:

```bash
python3 --version
# Should output Python 3.9.x or higher
```

### 2. Node.js Setup

We'll use Node.js 16+ for our frontend:

```bash
# For Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# For macOS using Homebrew
brew install node@16

# For Windows, download the installer from nodejs.org
```

Verify the installation:

```bash
node --version
# Should output v16.x.x or higher

npm --version
# Should output 8.x.x or higher
```

### 3. MongoDB Setup

Install MongoDB for database storage:

```bash
# For Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# For macOS using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# For Windows, download the installer from mongodb.com
```

Verify the installation:

```bash
mongo --version
# Should show MongoDB shell version information
```

### 4. Redis Setup

Install Redis for caching:

```bash
# For Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# For macOS using Homebrew
brew install redis
brew services start redis

# For Windows, download from redis.io or use WSL
```

Verify the installation:

```bash
redis-cli ping
# Should output PONG
```

### 5. Chrome Browser and ChromeDriver

Install Google Chrome and ChromeDriver for web automation:

```bash
# For Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# For macOS using Homebrew
brew install --cask google-chrome

# For Windows, download from google.com/chrome
```

For ChromeDriver, download the version matching your Chrome from [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads) and add it to your PATH.

### 6. Solana CLI Tools

Install Solana command line tools:

```bash
sh -c "$(curl -sSfL https://release.solana.com/v1.14.18/install)"
```

Add Solana to your PATH (the installer will provide instructions).

Verify the installation:

```bash
solana --version
# Should output Solana CLI version information
```

### 7. Docker Setup (Optional for development, necessary for deployment)

Install Docker and Docker Compose:

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# For macOS
brew install --cask docker

# For Windows, download Docker Desktop from docker.com
```

Verify the installation:

```bash
docker --version
docker-compose --version
# Should output version information
```

## Project Structure Setup

Now, let's create our project directory structure:

```bash
# Create the main project directory
mkdir solana-ai-agent-platform
cd solana-ai-agent-platform

# Create backend directory structure
mkdir -p backend/src/{agent,browser,blockchain,payment,api,models,utils,config}
mkdir -p backend/tests/{unit,integration}
touch backend/requirements.txt
touch backend/Dockerfile
touch backend/.env.example
touch backend/README.md

# Create frontend directory structure
mkdir -p frontend/src/{components,pages,hooks,utils,context,assets}
mkdir -p frontend/public
touch frontend/package.json
touch frontend/Dockerfile
touch frontend/.env.example
touch frontend/README.md

# Create deployment directory
mkdir -p deployment/{docker,kubernetes}
touch deployment/docker-compose.yml
touch deployment/.env.example
touch deployment/README.md

# Create documentation directory
mkdir -p docs/{api,deployment,development}
touch docs/README.md

# Create root configuration files
touch .gitignore
touch README.md
```

## Installing Dependencies

Let's install the necessary dependencies for both backend and frontend:

### Backend Dependencies

First, create a Python virtual environment:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

Now, create the `requirements.txt` file with the following content:

```
# Web Framework
fastapi==0.95.0
uvicorn==0.21.1
pydantic==1.10.7

# Database
pymongo==4.3.3
motor==3.1.1
redis==4.5.4

# AI and Machine Learning
smolagents==0.1.0
litellm==0.1.1
anthropic==0.3.6
openai==0.27.6

# Web Automation
selenium==4.9.0
helium==3.2.3
pillow==9.5.0

# Blockchain Integration
solana==0.30.0
anchorpy==0.15.0

# Utilities
python-dotenv==1.0.0
requests==2.28.2
aiohttp==3.8.4
websockets==11.0.2
pyjwt==2.6.0
pytest==7.3.1
black==23.3.0
isort==5.12.0
mypy==1.2.0
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Frontend Dependencies

Switch to the frontend directory:

```bash
cd ../frontend
```

Initialize a new React application with TypeScript:

```bash
npx create-react-app . --template typescript
```

Install additional frontend dependencies:

```bash
npm install \
  @solana/web3.js \
  @solana/wallet-adapter-react \
  @solana/wallet-adapter-react-ui \
  @solana/wallet-adapter-base \
  @solana/wallet-adapter-wallets \
  @metaplex-foundation/js \
  @metaplex-foundation/umi \
  @metaplex-foundation/umi-bundle-defaults \
  axios \
  react-query \
  tailwindcss \
  @headlessui/react \
  @heroicons/react \
  react-router-dom \
  socket.io-client \
  date-fns \
  uuid
```

Set up Tailwind CSS:

```bash
npx tailwindcss init -p
```

## Environment Configuration

Let's create our environment configuration files:

### Backend Environment (.env.example)

```bash
cd ../backend
```

Edit `.env.example`:

```
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=true
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/solana_ai_agent
REDIS_URI=redis://localhost:6379/0

# Authentication
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRATION=86400  # 24 hours in seconds

# AI Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
XAI_API_KEY=your_xai_api_key
OPEN_ROUTER_API_KEY=your_openrouter_api_key
DEFAULT_MODEL=anthropic/claude-3-opus-20240229

# Solana Configuration
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_WALLET_PATH=./key/wallet.json
NETWORK=devnet  # mainnet, testnet, devnet, localnet

# Birdeye API
BIRDEYE_API_KEY=your_birdeye_api_key

# Browser Automation
BROWSER_HEADLESS=false
CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# X402 Configuration
X402_FACILITATOR_URL=https://s402.w3hf.fun
X402_AUTO_APPROVE_THRESHOLD=0.1  # in USDC
```

Create your actual environment file:

```bash
cp .env.example .env
# Now edit .env with your actual configuration values
```

### Frontend Environment (.env.example)

```bash
cd ../frontend
```

Edit `.env.example`:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SOLANA_NETWORK=devnet
REACT_APP_SOLANA_RPC_URL=https://api.devnet.solana.com
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
```

Create your actual environment file:

```bash
cp .env.example .env
# Now edit .env with your actual configuration values
```

### .gitignore Setup

Finally, set up the `.gitignore` file to avoid committing sensitive information:

```bash
cd ..
```

Edit `.gitignore`:

```
# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
venv/
ENV/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp/
.pnp.js
coverage/
build/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Solana
.anchor/
target/
keypairs/
*.keypair.json
wallet.json

# Docker
.docker/
docker-compose.override.yml

# Logs
logs/
*.log
npm-debug.log*

# Testing
.coverage
htmlcov/
.pytest_cache/

# Miscellaneous
.tmp/
.temp/
tmp/
temp/
```

With your development environment now set up, you're ready to start building the SolanaAI Agent platform!
