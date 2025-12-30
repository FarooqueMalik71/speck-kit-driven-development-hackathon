from pydantic import BaseModel
from typing import Optional


class Example(BaseModel):
    """
    Represents an example in a textbook response
    """
    title: str
    description: str
    code: Optional[str] = None  # Code example if applicable