import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Query, status

from src.models.agent import AgentRunStatus
from src.models.user import User
from src.utils.auth import get_current_user
from .service import agent_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=Dict[str, Any])
async def run_agent(
    prompt: str = Body(...),
    model: Optional[str] = Body(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """
    Run the AI agent with a prompt.
    """
    try:
        run_id = await agent_service.start_agent_run(
            user_id=current_user.id,
            prompt=prompt,
            model=model or (current_user.preferences or {}).get("default_model", "default"),
            background_tasks=background_tasks
        )
        return {
            "success": True,
            "message": "Agent run started",
            "data": {"run_id": run_id}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting agent run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting agent run"
        )

@router.get("/run/{run_id}", response_model=Dict[str, Any])
async def get_agent_run(
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get an agent run by ID.
    """
    try:
        run = await agent_service.get_agent_run(run_id, current_user.id)
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent run not found"
            )
        return {
            "success": True,
            "message": "Agent run retrieved",
            "data": run
        }
    except Exception as e:
        logger.error(f"Error retrieving agent run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving agent run"
        )

@router.get("/runs", response_model=Dict[str, Any])
async def get_agent_runs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[AgentRunStatus] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of agent runs for the current user.
    """
    try:
        runs, total = await agent_service.get_agent_runs(
            user_id=current_user.id,
            page=page,
            limit=limit,
            status=status
        )
        return {
            "success": True,
            "message": "Agent runs retrieved",
            "data": {
                "runs": runs,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving agent runs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving agent runs"
        )

@router.delete("/run/{run_id}", response_model=Dict[str, Any])
async def cancel_agent_run(
    run_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an agent run.
    """
    try:
        success = await agent_service.cancel_agent_run(run_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent run not found or already completed"
            )
        return {
            "success": True,
            "message": "Agent run cancelled"
        }
    except Exception as e:
        logger.error(f"Error cancelling agent run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling agent run"
        ) 