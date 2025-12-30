from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .conversation_turn import ConversationTurn


class ConversationSession(BaseModel):
    """
    Represents a conversation session with history of exchanges
    """
    session_id: str  # UUID
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    user_id: Optional[str] = None  # Associated user ID if authenticated
    history: List[ConversationTurn] = []