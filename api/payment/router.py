from fastapi import APIRouter

router = APIRouter()

# Example placeholder endpoint for payment operations
@router.get("/status")
async def payment_status():
    return {"status": "payment module ready"} 