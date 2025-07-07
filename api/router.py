from fastapi import APIRouter

from .auth import router as auth_router
from .agent import router as agent_router
from .browser import router as browser_router
from .blockchain import router as blockchain_router
from .payment import router as payment_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agent_router, prefix="/agent", tags=["AI Agent"])
api_router.include_router(browser_router, prefix="/browser", tags=["Browser Automation"])
api_router.include_router(blockchain_router, prefix="/blockchain", tags=["Blockchain Operations"])
api_router.include_router(payment_router, prefix="/payment", tags=["Payments"]) 