"""
Streaming response models for TNSA API.
"""

from dataclasses import dataclass
from typing import Iterator, AsyncIterator, Optional, Dict, Any, Union
from .base import BaseModel
from .chat import ChatCompletionChunk
from .common import Usage


@dataclass
class StreamingResponse(BaseModel):
    """Base class for streaming responses."""
    id: str
    model: str
    
    def __iter__(self):
        """Make the response iterable."""
        return self
    
    def __next__(self):
        """Get next chunk in the stream."""
        raise NotImplementedError("Subclasses must implement __next__")


class StreamingStats(BaseModel):
    """Statistics for a completed streaming response."""
    
    def __init__(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        estimated_cost: float = 0.0,
        latency: float = 0.0,
        first_token_latency: Optional[float] = None,
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens or (prompt_tokens + completion_tokens)
        self.estimated_cost = estimated_cost
        self.latency = latency
        self.first_token_latency = first_token_latency
    
    def to_usage(self) -> Usage:
        """Convert to Usage object."""
        return Usage(
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.total_tokens,
            estimated_cost=self.estimated_cost
        )


class ChatCompletionStream:
    """Streaming chat completion response."""
    
    def __init__(
        self,
        stream_iterator: Union[Iterator[Dict[str, Any]], AsyncIterator[Dict[str, Any]]],
        response_id: str,
        model: str,
    ):
        self._stream_iterator = stream_iterator
        self.id = response_id
        self.model = model
        self._accumulated_content = ""
        self._stats: Optional[StreamingStats] = None
        self._is_async = hasattr(stream_iterator, '__aiter__')
    
    def __iter__(self) -> Iterator[ChatCompletionChunk]:
        """Iterate over streaming chunks."""
        if self._is_async:
            raise TypeError("Use 'async for' with async streams")
        
        for chunk_data in self._stream_iterator:
            chunk = self._process_chunk(chunk_data)
            if chunk:
                yield chunk
    
    def __aiter__(self) -> AsyncIterator[ChatCompletionChunk]:
        """Async iterate over streaming chunks."""
        if not self._is_async:
            raise TypeError("Use regular 'for' with sync streams")
        
        return self._aiter_impl()
    
    async def _aiter_impl(self) -> AsyncIterator[ChatCompletionChunk]:
        """Implementation of async iteration."""
        async for chunk_data in self._stream_iterator:
            chunk = self._process_chunk(chunk_data)
            if chunk:
                yield chunk
    
    def _process_chunk(self, chunk_data: Dict[str, Any]) -> Optional[ChatCompletionChunk]:
        """Process a raw chunk from the stream."""
        try:
            # Handle different chunk formats
            if "token" in chunk_data:
                # TNSA format with token field
                chunk = ChatCompletionChunk(
                    id=self.id,
                    model=self.model,
                    choices=[{
                        "index": 0,
                        "delta": {"content": chunk_data["token"]},
                        "finish_reason": None
                    }]
                )
                self._accumulated_content += chunk_data["token"]
                return chunk
            
            elif "stats" in chunk_data:
                # Statistics chunk
                stats_data = chunk_data["stats"]
                self._stats = StreamingStats(
                    prompt_tokens=stats_data.get("prompt_tokens", 0),
                    completion_tokens=stats_data.get("completion_tokens", 0),
                    estimated_cost=stats_data.get("cost", 0.0),
                    latency=float(stats_data.get("latency", 0.0)),
                    first_token_latency=float(stats_data.get("first_token", 0.0)) if stats_data.get("first_token") else None,
                )
                return None  # Don't yield stats as chunks
            
            elif "choices" in chunk_data:
                # OpenAI-compatible format
                chunk = ChatCompletionChunk.from_dict(chunk_data)
                if chunk.content:
                    self._accumulated_content += chunk.content
                return chunk
            
            elif "error" in chunk_data:
                # Error in stream
                from exceptions import TNSAError
                raise TNSAError(chunk_data["error"])
            
            return None
            
        except Exception as e:
            from exceptions import TNSAError
            raise TNSAError(f"Failed to process stream chunk: {e}")
    
    @property
    def accumulated_content(self) -> str:
        """Get all accumulated content from the stream."""
        return self._accumulated_content
    
    @property
    def stats(self) -> Optional[StreamingStats]:
        """Get streaming statistics if available."""
        return self._stats
    
    def collect(self) -> str:
        """Collect all content from the stream."""
        if self._is_async:
            raise TypeError("Use 'await collect_async()' with async streams")
        
        content = ""
        for chunk in self:
            if chunk.content:
                content += chunk.content
        return content
    
    async def collect_async(self) -> str:
        """Async collect all content from the stream."""
        if not self._is_async:
            raise TypeError("Use 'collect()' with sync streams")
        
        content = ""
        async for chunk in self:
            if chunk.content:
                content += chunk.content
        return content