from pydantic import BaseModel
from typing import Optional, List

class ProtectionResult(BaseModel):
    is_safe: bool
    reason: Optional[str] = None
    action: str = "allow"  # allow, block, sanitize, human_escalate
    sanitized_text: Optional[str] = None
    suggested_response: Optional[str] = None
    threat_level: str = "low" # low, medium, high
    detected_patterns: List[str] = []
