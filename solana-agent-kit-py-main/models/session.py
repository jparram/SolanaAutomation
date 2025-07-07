from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Session(BaseModel):
    id: str
    user_id: str
    token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    created_at: datetime
    last_activity: datetime 