import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Query, status

from src.models.agent import AgentRunStatus
from src.models.user import User
from src.utils.auth import get_current_user
from .service import browser_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/automate", response_model=Dict[str, Any])
async def run_browser_automation(
    instructions: str = Body(...),
    url: Optional[str] = Body(None),
    developer_mode: bool = Body(False),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """
    Run browser automation with instructions.
    """
    try:
        task_id = await browser_service.start_browser_task(
            user_id=current_user.id,
            instructions=instructions,
            url=url,
            developer_mode=developer_mode,
            headless=(current_user.preferences or {}).get("browser_headless", False),
            background_tasks=background_tasks
        )
        return {
            "success": True,
            "message": "Browser automation started",
            "data": {"task_id": task_id}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting browser automation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting browser automation"
        )

@router.get("/task/{task_id}", response_model=Dict[str, Any])
async def get_browser_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a browser task by ID.
    """
    try:
        task = await browser_service.get_browser_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Browser task not found"
            )
        return {
            "success": True,
            "message": "Browser task retrieved",
            "data": task
        }
    except Exception as e:
        logger.error(f"Error retrieving browser task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving browser task"
        )

@router.get("/tasks", response_model=Dict[str, Any])
async def get_browser_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[AgentRunStatus] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of browser tasks for the current user.
    """
    try:
        tasks, total = await browser_service.get_browser_tasks(
            user_id=current_user.id,
            page=page,
            limit=limit,
            status=status
        )
        return {
            "success": True,
            "message": "Browser tasks retrieved",
            "data": {
                "tasks": tasks,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving browser tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving browser tasks"
        )

@router.delete("/task/{task_id}", response_model=Dict[str, Any])
async def cancel_browser_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a browser task.
    """
    try:
        success = await browser_service.cancel_browser_task(task_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Browser task not found or already completed"
            )
        return {
            "success": True,
            "message": "Browser task cancelled"
        }
    except Exception as e:
        logger.error(f"Error cancelling browser task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling browser task"
        ) 