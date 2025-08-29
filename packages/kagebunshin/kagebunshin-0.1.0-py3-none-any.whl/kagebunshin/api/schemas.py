from typing import Optional, Any
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    first_query: Optional[str] = None
    headless: Optional[bool] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    user_data_dir: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str


class SendMessageRequest(BaseModel):
    text: str = Field(..., description="User message to process in this session")


class SessionStatus(BaseModel):
    session_id: str
    status: str  # idle|running|closed
    last_activity_at: Optional[str] = None
    current_url: Optional[str] = None
    current_title: Optional[str] = None
    actions_performed: Optional[int] = None
    error: Optional[str] = None


class StreamEvent(BaseModel):
    type: str
    text: Optional[str] = None
    name: Optional[str] = None
    args: Optional[Any] = None
    final_url: Optional[str] = None
    final_title: Optional[str] = None
    actions: Optional[int] = None


