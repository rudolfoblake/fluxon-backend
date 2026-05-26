from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class MessagePayload(BaseModel):
    message_id: str
    remote_jid: str
    push_name: Optional[str] = None
    text: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None # image, audio, video, document
    timestamp: datetime = Field(default_factory=datetime.now)

class LeadQualification(BaseModel):
    score: int = 0
    intent: str = "unknown"
    urgency: str = "low"
    signals: List[str] = []
    summary: Optional[str] = None

class AIResponse(BaseModel):
    content: str
    provider: str
    model: str
    raw_response: Optional[Any] = None
