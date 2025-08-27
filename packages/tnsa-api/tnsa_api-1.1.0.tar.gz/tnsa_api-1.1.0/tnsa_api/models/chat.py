"""
Chat completion models for TNSA API.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Literal
from .base import BaseModel, current_timestamp
from .common import Usage

MessageRole = Literal["system", "user", "assistant"]


@dataclass
class ChatMessage(BaseModel):
    """A chat message."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate message."""
        if self.role not in ["system", "user", "assistant"]:
            raise ValueError(f"Invalid role: {self.role}")
        
        if not self.content or not isinstance(self.content, str):
            raise ValueError("Message content must be a non-empty string")


@dataclass
class ChatCompletionChoice(BaseModel):
    """A choice in a chat completion response."""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionChoice':
        """Create from dictionary with nested message."""
        message_data = data.get("message", {})
        message = ChatMessage.from_dict(message_data)
        
        return cls(
            index=data["index"],
            message=message,
            finish_reason=data.get("finish_reason")
        )


@dataclass
class ChatCompletion(BaseModel):
    """Chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int = 0
    model: str = ""
    choices: List[ChatCompletionChoice] = None
    usage: Optional[Usage] = None
    conversation_id: Optional[str] = None
    
    def __post_init__(self):
        """Set default values."""
        if self.created == 0:
            self.created = current_timestamp()
        
        if self.choices is None:
            self.choices = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletion':
        """Create from dictionary with nested objects."""
        choices = [
            ChatCompletionChoice.from_dict(choice_data)
            for choice_data in data.get("choices", [])
        ]
        
        usage = None
        if "usage" in data:
            usage = Usage.from_dict(data["usage"])
        
        return cls(
            id=data["id"],
            object=data.get("object", "chat.completion"),
            created=data.get("created", current_timestamp()),
            model=data["model"],
            choices=choices,
            usage=usage,
            conversation_id=data.get("conversation_id")
        )
    
    @property
    def content(self) -> Optional[str]:
        """Get the content of the first choice."""
        if self.choices:
            return self.choices[0].message.content
        return None


@dataclass
class ChatCompletionDelta(BaseModel):
    """Delta for streaming chat completion."""
    role: Optional[str] = None
    content: Optional[str] = None


@dataclass
class ChatCompletionChunkChoice(BaseModel):
    """A choice in a streaming chat completion chunk."""
    index: int
    delta: ChatCompletionDelta
    finish_reason: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionChunkChoice':
        """Create from dictionary with nested delta."""
        delta_data = data.get("delta", {})
        delta = ChatCompletionDelta.from_dict(delta_data)
        
        return cls(
            index=data["index"],
            delta=delta,
            finish_reason=data.get("finish_reason")
        )


@dataclass
class ChatCompletionChunk(BaseModel):
    """Streaming chat completion chunk."""
    id: str
    object: str = "chat.completion.chunk"
    created: int = 0
    model: str = ""
    choices: List[ChatCompletionChunkChoice] = None
    
    def __post_init__(self):
        """Set default values."""
        if self.created == 0:
            self.created = current_timestamp()
        
        if self.choices is None:
            self.choices = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionChunk':
        """Create from dictionary with nested objects."""
        choices = [
            ChatCompletionChunkChoice.from_dict(choice_data)
            for choice_data in data.get("choices", [])
        ]
        
        return cls(
            id=data["id"],
            object=data.get("object", "chat.completion.chunk"),
            created=data.get("created", current_timestamp()),
            model=data["model"],
            choices=choices
        )
    
    @property
    def content(self) -> Optional[str]:
        """Get the content delta of the first choice."""
        if self.choices:
            return self.choices[0].delta.content
        return None