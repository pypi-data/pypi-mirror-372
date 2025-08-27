"""
TNSA API Python Client

A powerful, OpenAI-compatible Python SDK for TNSA NGen3 Pro and Lite Models
with MCP (Machine Control Protocol) integration.
"""

from .client import TNSA
from .async_client import AsyncTNSA
from .exceptions import (
    TNSAError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    InvalidRequestError,
    APIConnectionError,
    APITimeoutError,
)
from .models.chat import (
    ChatMessage,
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionDelta,
)
from .models.common import (
    Usage,
    Model,
    ModelPricing,
    Conversation,
)

# MCP (Machine Control Protocol) client
from .mcp import MCPClient
from .mcp.exceptions import (
    MCPError,
    MCPConnectionError,
    MCPAuthenticationError,
    MCPServerError,
    MCPToolNotFoundError,
    MCPInvalidParametersError,
)

__version__ = "1.1.0"  # Bump version for MCP integration
__author__ = "TNSA AI"
__email__ = "info@tnsaai.com"

__all__ = [
    # Core clients
    "TNSA",
    "AsyncTNSA",
    "MCPClient",
    
    # Core exceptions
    "TNSAError",
    "AuthenticationError", 
    "RateLimitError",
    "ModelNotFoundError",
    "InvalidRequestError",
    "APIConnectionError",
    "APITimeoutError",
    
    # MCP exceptions
    "MCPError",
    "MCPConnectionError",
    "MCPAuthenticationError",
    "MCPServerError",
    "MCPToolNotFoundError",
    "MCPInvalidParametersError",
    
    # Models
    "ChatMessage",
    "ChatCompletion",
    "ChatCompletionChoice",
    "Usage",
    "Model",
    "ModelPricing",
    "Conversation",
]