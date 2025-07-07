# Part 2: Building the Backend

In this section, we'll build the backend server for our SolanaAI Agent platform.

## Setting Up Server

First, let's set up the core server structure using FastAPI, which provides high performance and easy-to-use API development.

### 1. Create Config Module

Create a configuration module to load environment variables:

```bash
cd backend/src/config
touch __init__.py
touch settings.py
```

Edit `settings.py`:

```python
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
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')

# X402 settings
X402_FACILITATOR_URL = os.getenv('X402_FACILITATOR_URL', 'https://s402.w3hf.fun')
X402_AUTO_APPROVE_THRESHOLD = float(os.getenv('X402_AUTO_APPROVE_THRESHOLD', '0.1'))

# Set environment variables for third-party libraries
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY
```

### 2. Create Database Connection Module

Let's set up database connections:

```bash
cd ../utils
touch __init__.py
touch database.py
```

Edit `database.py`:

```python
import asyncio
from typing import Optional

import motor.motor_asyncio
import redis.asyncio as redis
from pymongo import MongoClient

from ..config import settings

# MongoDB Connection
class MongoDB:
    client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls):
        if cls.client is None:
            cls.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
            cls.db = cls.client.get_database()
            
            # Create indexes
            await cls.create_indexes()
            
            print("Connected to MongoDB")
    
    @classmethod
    async def disconnect(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            print("Disconnected from MongoDB")
    
    @classmethod
    async def create_indexes(cls):
        # Create indexes for collections
        await cls.db.users.create_index("email", unique=True)
        await cls.db.sessions.create_index("token", unique=True)
        await cls.db.agent_runs.create_index("user_id")

# Redis Connection
class RedisDB:
    client: Optional[redis.Redis] = None
    
    @classmethod
    async def connect(cls):
        if cls.client is None:
            cls.client = redis.from_url(settings.REDIS_URI)
            # Check connection
            await cls.client.ping()
            print("Connected to Redis")
    
    @classmethod
    async def disconnect(cls):
        if cls.client is not None:
            await cls.client.close()
            cls.client = None
            print("Disconnected from Redis")

# Sync MongoDB client for non-async contexts
def get_sync_mongo_client():
    return MongoClient(settings.MONGODB_URI)

# Database initialization function
async def initialize_db():
    await MongoDB.connect()
    await RedisDB.connect()

# Database shutdown function
async def shutdown_db():
    await MongoDB.disconnect()
    await RedisDB.disconnect()
```

### 3. Create Data Models

Set up the Pydantic models for our API:

```bash
cd ../models
touch __init__.py
touch user.py
touch agent.py
touch session.py
touch common.py
```

Edit `common.py`:

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    page: int
    total_pages: int
    total_items: int
    items_per_page: int
    items: List[Any]


class SolanaNetwork(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"
    LOCALNET = "localnet"
```

Edit `user.py`:

```python
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field

from .common import SolanaNetwork


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserWallet(BaseModel):
    address: str
    label: Optional[str] = None
    is_default: bool = False
    network: SolanaNetwork = SolanaNetwork.DEVNET


class UserProfile(BaseModel):
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    twitter_handle: Optional[str] = None
    discord_handle: Optional[str] = None


class UserPreferences(BaseModel):
    default_model: Optional[str] = None
    default_network: SolanaNetwork = SolanaNetwork.DEVNET
    auto_approve_threshold: float = 0.1
    browser_headless: bool = False
    receive_email_notifications: bool = True
    receive_push_notifications: bool = True


class User(UserBase):
    id: str = Field(..., alias="_id")
    wallets: List[UserWallet] = []
    profile: Optional[UserProfile] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
```

Edit `session.py`:

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Session(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    created_at: datetime
    last_activity: datetime

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
```

Edit `agent.py`:

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStep(BaseModel):
    step_number: int
    step_type: str
    content: str
    timestamp: datetime
    observations: Optional[str] = None
    observation_images: Optional[List[str]] = None


class AgentRun(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    prompt: str
    status: AgentRunStatus
    steps: List[AgentStep] = []
    result: Optional[str] = None
    error: Optional[str] = None
    model: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    payment_info: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True


class BrowserTask(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    instructions: str
    url: Optional[str] = None
    status: AgentRunStatus
    result: Optional[str] = None
    error: Optional[str] = None
    screenshots: List[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
```

### 4. Create Main Application

Now, let's create the main FastAPI application:

```bash
cd ../../
touch main.py
```

Edit `main.py`:

```python
import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.utils.database import initialize_db, shutdown_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up server...")
    await initialize_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down server...")
    await shutdown_db()

# Create FastAPI application
app = FastAPI(
    title="SolanaAI Agent API",
    description="API for SolanaAI Agent platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "SolanaAI Agent API",
        "version": "1.0.0",
        "status": "online",
        "environment": settings.ENVIRONMENT,
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
```

### 5. Create Utilities for JWT Authentication

Let's create utilities for JWT token authentication:

```bash
cd src/utils
touch auth.py
```

Edit `auth.py`:

```python
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import DecodeError, ExpiredSignatureError
from pydantic import ValidationError

from ..config import settings
from ..models.session import Session
from ..models.user import User
from .database import MongoDB

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Function to create JWT token
def create_jwt_token(user_id: str) -> str:
    expires_delta = timedelta(seconds=settings.JWT_EXPIRATION)
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

# Function to decode JWT token
def decode_jwt_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if session exists and is valid
        session = await MongoDB.db.sessions.find_one({"token": token})
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if session has expired
        if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user_data = await MongoDB.db.users.find_one({"_id": user_id})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last activity
        await MongoDB.db.sessions.update_one(
            {"token": token},
            {"$set": {"last_activity": datetime.utcnow().isoformat()}}
        )
        
        return User(**user_data)
    
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to get current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user
```

### 6. Create Password Utility

Create a utility for password hashing:

```bash
touch password.py
```

Edit `password.py`:

```python
import secrets
import string
from typing import Tuple

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The password to hash
        
    Returns:
        str: The hashed password
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain-text password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random password.
    
    Args:
        length: The length of the password to generate
        
    Returns:
        str: The generated password
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password
```

With the core server setup complete, in the next sections we will implement the API endpoints, agent modules, and other functionality.
