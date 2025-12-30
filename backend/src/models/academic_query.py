from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AcademicQuery(BaseModel):
    """
    Represents a user's question or request for academic information
    """
    query_id: str  # UUID
    session_id: str
    content: str
    timestamp: datetime
    processed_content: Optional[str] = None  # Cleaned/rephrased query content
    intent: Optional[str] = None  # Detected user intent from ambiguous input