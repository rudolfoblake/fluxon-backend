from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class EvolutionWebhookPayload(BaseModel):
    event: str
    instance: str
    data: Dict[str, Any]
    destination: Optional[str] = None
    date_time: str
    sender: str
    server_url: str
    apikey: str
