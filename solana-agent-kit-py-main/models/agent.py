from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentRun(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    prompt: str
    status: AgentRunStatus
    steps: List[Dict[str, Any]] = []
    result: Optional[str] = None
    error: Optional[str] = None
    model: str
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    payment_info: Optional[Dict[str, Any]] = None

class BrowserTask(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    instructions: str
    url: Optional[str] = None
    status: AgentRunStatus
    screenshots: List[str] = []
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    developer_mode: bool = False 