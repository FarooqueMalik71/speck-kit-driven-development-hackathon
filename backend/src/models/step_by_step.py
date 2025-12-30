from pydantic import BaseModel
from typing import List
from .step import Step


class StepByStep(BaseModel):
    """
    Represents a step-by-step explanation in a textbook response
    """
    title: str  # Title of the process being explained
    steps: List[Step]  # Ordered list of steps