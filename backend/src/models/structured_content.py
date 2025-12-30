from pydantic import BaseModel
from typing import List, Optional
from .definition import Definition
from .example import Example
from .step_by_step import StepByStep


class StructuredContent(BaseModel):
    """
    Represents structured elements of a textbook response
    """
    headings: List[str] = []
    bullet_points: List[str] = []
    definitions: List[Definition] = []
    examples: List[Example] = []
    step_by_step: Optional[StepByStep] = None  # Step-by-step explanations if applicable