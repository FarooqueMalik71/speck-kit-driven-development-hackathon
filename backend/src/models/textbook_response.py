from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .structured_content import StructuredContent
from .reference import Reference


class TextbookResponse(BaseModel):
    """
    Structured response containing headings, bullet points, definitions, examples, citations, and reference links
    """
    response_id: str  # UUID
    query_id: str
    session_id: str
    content: str  # The formatted response content
    structured_content: Optional[StructuredContent] = None  # Parsed structured elements
    references: List[Reference] = []  # List of references provided
    timestamp: datetime
    confidence: float  # Confidence score for the response (0-1)
    is_contextual: bool = False  # Whether this response used conversation context