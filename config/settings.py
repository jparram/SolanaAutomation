import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Server settings
PORT = int(os.getenv('PORT', '8000'))
HOST = os.getenv('HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

# Database settings
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/solana_ai_agent')
REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379/0')

# Authentication settings
JWT_SECRET = os.getenv('JWT_SECRET', 'your_jwt_secret_key')
JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', '86400'))

# AI settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
XAI_API_KEY = os.getenv('XAI_API_KEY', '')
OPEN_ROUTER_API_KEY = os.getenv('OPEN_ROUTER_API_KEY', '')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'anthropic/claude-3-opus-20240229')

# Solana settings
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.devnet.solana.com')
SOLANA_WALLET_PATH = os.getenv('SOLANA_WALLET_PATH', './key/wallet.json')
NETWORK = os.getenv('NETWORK', 'devnet')

# Birdeye API
BIRDEYE_API_KEY = os.getenv('BIRDEYE_API_KEY', '')

# Browser automation settings
BROWSER_HEADLESS = os.getenv('BROWSER_HEADLESS', 'False').lower() == 'true' 