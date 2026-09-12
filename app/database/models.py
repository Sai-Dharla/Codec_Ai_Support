from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class SessionModel:
    session_id: str
    created_at: datetime
    last_active: datetime
    context_topic: Optional[str] = None

@dataclass
class InteractionModel:
    id: Optional[int]
    session_id: str
    user_message: str
    bot_response: str
    intent_detected: Optional[str]
    confidence: Optional[float]
    context_topic: Optional[str]
    timestamp: datetime

