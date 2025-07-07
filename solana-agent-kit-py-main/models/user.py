from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    username: str
    wallets: Optional[List[Dict[str, Any]]] = []
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_verified: bool = False 