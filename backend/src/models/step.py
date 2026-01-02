from pydantic import BaseModel
from typing import Optional


class Step(BaseModel):
    """
    Represents a single step in a step-by-step explanation
    """
    step_number: int  # The sequence number
    description: str  # Description of this step
    example: Optional[str] = None  # Example for this step