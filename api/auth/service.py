import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple

from src.config import settings
from src.models.user import UserCreate, UserLogin
from src.utils.auth import create_jwt_token
from src.utils.database import MongoDB
from src.utils.password import hash_password, verify_password

logger = logging.getLogger(__name__)

class AuthService:
    async def register_user(self, user_data: UserCreate) -> Dict:
        # Check if email already exists
        existing_user = await MongoDB.db.users.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already registered")
        # Hash password
        hashed_password = hash_password(user_data.password)
        # Create user document
        now = datetime.utcnow()
        user_id = str(uuid.uuid4())
        user_doc = {
            "_id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "password": hashed_password,
            "wallets": [],
            "profile": None,
            "preferences": {
                "default_model": settings.DEFAULT_MODEL,
                "default_network": "devnet",
                "auto_approve_threshold": 0.1,
                "browser_headless": False,
                "receive_email_notifications": True,
                "receive_push_notifications": True
            },
            "is_active": True,
            "is_verified": False,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        await MongoDB.db.users.insert_one(user_doc)
        user_doc.pop("password")
        return user_doc

    async def login_user(self, user_login: UserLogin) -> Tuple[str, Dict]:
        user = await MongoDB.db.users.find_one({"email": user_login.email})
        if not user:
            raise ValueError("Invalid email or password")
        if not verify_password(user_login.password, user["password"]):
            raise ValueError("Invalid email or password")
        if not user.get("is_active", True):
            raise ValueError("User account is inactive")
        token = create_jwt_token(user["_id"])
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=settings.JWT_EXPIRATION)
        session_id = str(uuid.uuid4())
        session_doc = {
            "_id": session_id,
            "user_id": user["_id"],
            "token": token,
            "expires_at": expires_at.isoformat(),
            "created_at": now.isoformat(),
            "last_activity": now.isoformat()
        }
        await MongoDB.db.sessions.insert_one(session_doc)
        user.pop("password")
        return token, user

    async def logout_user(self, user_id: str):
        await MongoDB.db.sessions.delete_many({"user_id": user_id})

auth_service = AuthService() 