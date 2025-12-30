from pydantic import BaseModel
from typing import List, Optional
from .textbook_response import TextbookResponse
from .structured_content import StructuredContent
from .reference import Reference


class QueryRequest(BaseModel):
    """Request model for querying the textbook"""
    query: str
    session_id: Optional[str] = None  # If not provided, creates new session
    context_ids: List[str] = []
    mode: str = "full_book"  # "full_book" or "selected_text"


class QueryResponse(BaseModel):
    """Response model for textbook queries"""
    response_id: Optional[str] = None
    session_id: str
    answer: str
    citations: List[str] = []
    confidence: float = 0.0
    is_confident: bool = False
    sources: List[str] = []
    boundary_compliance: float = 0.0
    needs_fact_check: bool = False
    references: List[Reference] = []
    structured_content: Optional[StructuredContent] = None