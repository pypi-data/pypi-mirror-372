"""
Text completion models for TNSA API.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .base import BaseModel, current_timestamp
from .common import Usage


@dataclass
class TextCompletionChoice(BaseModel):
    """A choice in a text completion response."""
    index: int
    text: str
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None


@dataclass
class TextCompletion(BaseModel):
    """Text completion response."""
    id: str
    object: str = "text_completion"
    created: int = 0
    model: str = ""
    choices: List[TextCompletionChoice] = None
    usage: Optional[Usage] = None
    
    def __post_init__(self):
        """Set default values."""
        if self.created == 0:
            self.created = current_timestamp()
        
        if self.choices is None:
            self.choices = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextCompletion':
        """Create from dictionary with nested objects."""
        choices = [
            TextCompletionChoice.from_dict(choice_data)
            for choice_data in data.get("choices", [])
        ]
        
        usage = None
        if "usage" in data:
            usage = Usage.from_dict(data["usage"])
        
        return cls(
            id=data["id"],
            object=data.get("object", "text_completion"),
            created=data.get("created", current_timestamp()),
            model=data["model"],
            choices=choices,
            usage=usage
        )
    
    @property
    def text(self) -> Optional[str]:
        """Get the text of the first choice."""
        if self.choices:
            return self.choices[0].text
        return None