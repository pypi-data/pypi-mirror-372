"""
Base model classes for TNSA API.
"""

import json
from typing import Any, Dict, Type, TypeVar, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

T = TypeVar('T', bound='BaseModel')


@dataclass
class BaseModel:
    """Base class for all TNSA API models."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        # Filter out unknown fields
        field_names = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create model instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}({self.to_dict()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return self.__str__()


def current_timestamp() -> int:
    """Get current Unix timestamp."""
    return int(datetime.now().timestamp())