import logging
from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.models.user import User, UserCreate, UserLogin
from src.utils.auth import get_current_user
from .service import auth_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate = Body(...)):
    """
    Register a new user.
    """
    try:
        user = await auth_service.register_user(user_data)
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {"user_id": user["_id"]}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )

@router.post("/login", response_model=Dict[str, Any])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and return a token.
    """
    try:
        user_login = UserLogin(email=form_data.username, password=form_data.password)
        token, user = await auth_service.login_user(user_login)
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["_id"],
                    "email": user["email"],
                    "username": user["username"]
                }
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging in"
        )

@router.post("/logout", response_model=Dict[str, Any])
async def logout(current_user: User = Depends(get_current_user)):
    """
    Log out a user by invalidating their token.
    """
    try:
        await auth_service.logout_user(current_user.id)
        return {
            "success": True,
            "message": "Logout successful"
        }
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging out"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current user's information.
    """
    try:
        user_data = {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "wallets": current_user.wallets,
            "profile": current_user.profile,
            "preferences": current_user.preferences,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified
        }
        return {
            "success": True,
            "message": "User retrieved successfully",
            "data": user_data
        }
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        ) 