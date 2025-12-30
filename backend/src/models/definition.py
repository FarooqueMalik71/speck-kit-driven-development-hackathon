from pydantic import BaseModel
from typing import Optional


class Definition(BaseModel):
    """
    Represents a term definition in a textbook response
    """
    term: str
    definition: str
    context: Optional[str] = None  # Context where this definition is relevant