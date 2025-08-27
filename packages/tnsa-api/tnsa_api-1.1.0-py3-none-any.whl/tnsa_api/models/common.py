"""
Common data models used across TNSA API.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .base import BaseModel, current_timestamp


@dataclass
class Usage(BaseModel):
    """Token usage and cost information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    
    def __post_init__(self):
        """Validate and compute derived fields."""
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            self.total_tokens = self.prompt_tokens + self.completion_tokens


@dataclass
class ModelPricing(BaseModel):
    """Model pricing information."""
    input_cost_per_million: float
    output_cost_per_million: float
    currency: str = "USD"
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for given token usage."""
        input_cost = (prompt_tokens / 1_000_000) * self.input_cost_per_million
        output_cost = (completion_tokens / 1_000_000) * self.output_cost_per_million
        return input_cost + output_cost


@dataclass
class Model(BaseModel):
    """Model information."""
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "tnsa"
    capabilities: List[str] = None
    context_length: int = 4096
    pricing: Optional[ModelPricing] = None
    
    def __post_init__(self):
        """Set default values."""
        if self.capabilities is None:
            self.capabilities = ["chat", "completion"]
        
        if self.pricing is None:
            # Default pricing - will be updated from API
            self.pricing = ModelPricing(
                input_cost_per_million=1.0,
                output_cost_per_million=2.0
            )
    
    def supports_capability(self, capability: str) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.capabilities
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for token usage with this model."""
        if self.pricing:
            return self.pricing.calculate_cost(prompt_tokens, completion_tokens)
        return 0.0


@dataclass
class Conversation(BaseModel):
    """Conversation with message history and metadata."""
    id: str
    model: str
    created: int
    messages: List[Dict[str, Any]]
    total_tokens: int = 0
    total_cost: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Set default values."""
        if self.metadata is None:
            self.metadata = {}
    
    def add_message(self, role: str, content: str, tokens: int = 0, cost: float = 0.0):
        """Add a message to the conversation."""
        message = {
            "role": role,
            "content": content,
            "timestamp": current_timestamp(),
        }
        self.messages.append(message)
        self.total_tokens += tokens
        self.total_cost += cost
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Get messages formatted for API requests."""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]
    
    def truncate_to_limit(self, token_limit: int, preserve_system: bool = True) -> None:
        """Truncate conversation to fit within token limit."""
        if self.total_tokens <= token_limit:
            return
        
        # Simple truncation strategy: keep system message and recent messages
        system_messages = []
        other_messages = []
        
        for msg in self.messages:
            if msg["role"] == "system" and preserve_system:
                system_messages.append(msg)
            else:
                other_messages.append(msg)
        
        # Keep recent messages that fit within limit
        # This is a simplified approach - in practice, you'd want more sophisticated truncation
        estimated_tokens_per_message = self.total_tokens // len(self.messages) if self.messages else 0
        max_messages = max(1, token_limit // max(1, estimated_tokens_per_message))
        
        if preserve_system:
            self.messages = system_messages + other_messages[-max_messages:]
        else:
            self.messages = other_messages[-max_messages:]
        
        # Recalculate totals (simplified)
        self.total_tokens = len(self.messages) * estimated_tokens_per_message
        self.total_cost = self.total_cost * (len(self.messages) / len(other_messages + system_messages))


