from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .reference import Reference


class ConversationTurn(BaseModel):
    """
    Represents a single turn in a conversation (user or assistant)
    """
    turn_id: str  # UUID
    timestamp: datetime
    role: str  # "user" | "assistant"
    content: str
    context: Optional[str] = None  # Additional context used for this turn
    references: List[Reference] = []