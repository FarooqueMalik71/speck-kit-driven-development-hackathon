from pydantic import BaseModel
from typing import Optional


class Reference(BaseModel):
    """
    Represents a reference link for academic content
    """
    type: str  # "internal" | "external"
    title: str
    url: str
    description: str
    relevance: float  # How relevant this reference is to the query (0-1)