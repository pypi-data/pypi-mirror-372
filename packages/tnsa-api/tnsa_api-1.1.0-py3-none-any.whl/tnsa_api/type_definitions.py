"""
Type definitions for TNSA API client.
"""

from typing import Dict, List, Any, Union, Optional, Literal
from typing_extensions import TypedDict, NotRequired

# Message types
MessageRole = Literal["system", "user", "assistant"]

class MessageDict(TypedDict):
    role: MessageRole
    content: str
    name: NotRequired[str]

# Request types
class ChatCompletionRequest(TypedDict):
    model: str
    messages: List[MessageDict]
    temperature: NotRequired[float]
    max_tokens: NotRequired[int]
    top_p: NotRequired[float]
    stream: NotRequired[bool]
    stop: NotRequired[Union[str, List[str]]]
    conversation_id: NotRequired[str]

class CompletionRequest(TypedDict):
    model: str
    prompt: str
    temperature: NotRequired[float]
    max_tokens: NotRequired[int]
    top_p: NotRequired[float]
    stream: NotRequired[bool]
    stop: NotRequired[Union[str, List[str]]]

# Response types
class UsageDict(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float

class ModelDict(TypedDict):
    id: str
    object: str
    created: int
    owned_by: str
    capabilities: List[str]
    context_length: int
    pricing: Dict[str, float]

class ChatCompletionChoiceDict(TypedDict):
    index: int
    message: MessageDict
    finish_reason: Optional[str]

class ChatCompletionDict(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoiceDict]
    usage: UsageDict
    conversation_id: NotRequired[str]

# Streaming types
class ChatCompletionDeltaDict(TypedDict):
    role: NotRequired[str]
    content: NotRequired[str]

class ChatCompletionChunkChoiceDict(TypedDict):
    index: int
    delta: ChatCompletionDeltaDict
    finish_reason: Optional[str]

class ChatCompletionChunkDict(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChunkChoiceDict]

# Configuration types
class ConfigDict(TypedDict):
    api_key: str
    base_url: str
    timeout: float
    max_retries: int
    default_model: str
    log_level: str

# Error types
class ErrorDict(TypedDict):
    message: str
    type: str
    param: NotRequired[str]
    code: NotRequired[str]

class ErrorResponseDict(TypedDict):
    error: ErrorDict