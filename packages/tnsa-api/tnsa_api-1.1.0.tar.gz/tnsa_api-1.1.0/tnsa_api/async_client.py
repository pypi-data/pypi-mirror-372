"""
Asynchronous TNSA API client implementation.
"""

from typing import Optional, Dict, Any, List, Union, AsyncIterator
from .config import Config
from .http_client import AsyncHTTPClient
from .mcp.async_client import AsyncMCPClient
from .models.chat import (
    ChatMessage,
    ChatCompletion,
    ChatCompletionChunk,
)
from .models.common import (
    Model,
    Usage,
    Conversation,
)
from .models.streaming import ChatCompletionStream
from .exceptions import TNSAError, ModelNotFoundError


class AsyncChatCompletions:
    """Async chat completions interface."""
    
    def __init__(self, client: AsyncHTTPClient):
        self._client = client
    
    async def acreate(
        self,
        model: str,
        messages: List[Union[Dict[str, str], ChatMessage]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> Union[ChatCompletion, ChatCompletionStream]:
        """
        Create a chat completion asynchronously.
        
        Args:
            model: Model to use for completion
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            stream: Whether to stream the response
            stop: Stop sequences
            conversation_id: ID for conversation tracking
            **kwargs: Additional parameters
            
        Returns:
            ChatCompletion or ChatCompletionStream
        """
        # Convert messages to proper format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    "name": msg.name
                })
            elif isinstance(msg, dict):
                formatted_messages.append(msg)
            else:
                raise ValueError(f"Invalid message type: {type(msg)}")
        
        # Build request payload - TNSA API expects 'prompt' field
        payload = {
            "model": model,
            "prompt": self._format_messages_as_prompt(formatted_messages),
            "format": "html",  # TNSA API format
        }
        
        # Add optional parameters
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if stop is not None:
            payload["stop"] = stop
        if conversation_id is not None:
            payload["chat_id"] = conversation_id
        
        # Add any additional kwargs
        payload.update(kwargs)
        
        if stream:
            # Return streaming response
            stream_iterator = await self._client.post("/infer", data=payload, stream=True)
            return ChatCompletionStream(
                stream_iterator=stream_iterator,
                response_id=f"chatcmpl-{conversation_id or 'stream'}",
                model=model,
            )
        else:
            # Return regular response
            response_data = await self._client.post("/infer", data=payload)
            return self._parse_chat_completion(response_data, model)
    
    # Alias for consistency with OpenAI API
    create = acreate
    
    def _format_messages_as_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format messages as a single prompt for models that expect it."""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n".join(prompt_parts)
    
    def _parse_chat_completion(self, response_data: Dict[str, Any], model: str) -> ChatCompletion:
        """Parse TNSA API response into ChatCompletion."""
        # Handle TNSA API response format
        if "response" in response_data:
            # TNSA format
            message = ChatMessage(
                role="assistant",
                content=response_data["response"]
            )
            
            from .models.chat import ChatCompletionChoice
            choice = ChatCompletionChoice(
                index=0,
                message=message,
                finish_reason="stop"
            )
            
            usage = Usage(
                prompt_tokens=response_data.get("prompt_tokens", 0),
                completion_tokens=response_data.get("completion_tokens", 0),
                total_tokens=response_data.get("prompt_tokens", 0) + response_data.get("completion_tokens", 0),
                estimated_cost=response_data.get("cost", 0.0)
            )
            
            return ChatCompletion(
                id=response_data.get("chat_id", "chatcmpl-unknown"),
                model=model,
                choices=[choice],
                usage=usage,
                conversation_id=response_data.get("chat_id")
            )
        else:
            # OpenAI-compatible format
            return ChatCompletion.from_dict(response_data)


class AsyncModels:
    """Async models interface."""
    
    def __init__(self, client: AsyncHTTPClient):
        self._client = client
        self._cached_models: Optional[List[Model]] = None
    
    async def alist(self) -> List[Model]:
        """List available models asynchronously."""
        if self._cached_models is None:
            response_data = await self._client.get("/models")
            models_list = response_data.get("models", [])
            
            self._cached_models = []
            for model_id in models_list:
                model = Model(
                    id=model_id,
                    object="model",
                    created=0,
                    owned_by="tnsa",
                    capabilities=self._get_model_capabilities(model_id),
                    context_length=self._get_model_context_length(model_id),
                )
                self._cached_models.append(model)
        
        return self._cached_models
    
    async def aretrieve(self, model_id: str) -> Model:
        """Get details about a specific model asynchronously."""
        models = await self.alist()
        for model in models:
            if model.id == model_id:
                return model
        
        raise ModelNotFoundError(
            f"Model '{model_id}' not found",
            model_name=model_id,
            available_models=[m.id for m in models]
        )
    
    # Aliases for consistency
    list = alist
    retrieve = aretrieve
    
    def _get_model_capabilities(self, model_id: str) -> List[str]:
        """Get capabilities for a model."""
        if "Pro" in model_id:
            return ["chat", "completion", "reasoning"]
        elif "Lite" in model_id:
            return ["chat", "completion"]
        elif "Farmvaidya" in model_id:
            return ["chat", "agriculture"]
        else:
            return ["chat", "completion"]
    
    def _get_model_context_length(self, model_id: str) -> int:
        """Get context length for a model."""
        if "NGen3.9" in model_id:
            return 40000
        elif "NGen3-7B" in model_id:
            return 4096
        else:
            return 4096


class AsyncConversations:
    """Async conversations interface."""
    
    def __init__(self, client: AsyncHTTPClient):
        self._client = client
        self._conversations: Dict[str, Conversation] = {}
    
    async def acreate(
        self,
        model: str,
        system_prompt: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation asynchronously."""
        import uuid
        from .models.base import current_timestamp
        
        conversation_id = str(uuid.uuid4())
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
                "timestamp": current_timestamp()
            })
        
        conversation = Conversation(
            id=conversation_id,
            model=model,
            created=current_timestamp(),
            messages=messages
        )
        
        self._conversations[conversation_id] = conversation
        return conversation
    
    async def aget(self, conversation_id: str) -> Conversation:
        """Retrieve an existing conversation asynchronously."""
        if conversation_id not in self._conversations:
            raise TNSAError(f"Conversation '{conversation_id}' not found")
        
        return self._conversations[conversation_id]
    
    async def alist(self, limit: int = 20) -> List[Conversation]:
        """List user's conversations asynchronously."""
        conversations = list(self._conversations.values())
        conversations.sort(key=lambda c: c.created, reverse=True)
        return conversations[:limit]
    
    async def adelete(self, conversation_id: str) -> bool:
        """Delete a conversation asynchronously."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False
    
    # Aliases for consistency
    create = acreate
    get = aget
    list = alist
    delete = adelete


class AsyncTNSA:
    """
    Asynchronous TNSA API client.
    
    Usage:
        async with AsyncTNSA(api_key="your-api-key") as client:
            # List models
            models = await client.models.list()
            
            # Create chat completion
            response = await client.chat.completions.create(
                model="NGen3.9-Pro",
                messages=[{"role": "user", "content": "Hello!"}]
            )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        default_headers: Optional[Dict[str, str]] = None,
        config_file: Optional[str] = None,
    ):
        """
        Initialize async TNSA client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API (default: https://api.tnsaai.com)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            default_headers: Additional headers to include
            config_file: Path to configuration file
        """
        self.config = Config(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            config_file=config_file,
        )
        
        self._http_client = AsyncHTTPClient(self.config)
        
        # Initialize interfaces
        self._chat = AsyncChatCompletions(self._http_client)
        self._models = AsyncModels(self._http_client)
        self._conversations = AsyncConversations(self._http_client)
        
        # Lazy initialization of MCP client
        self._mcp_client = None
    
    @property
    def chat(self) -> AsyncChatCompletions:
        """Access to chat completion endpoints."""
        return self._chat
    
    @property
    def models(self) -> AsyncModels:
        """Access to model management endpoints."""
        return self._models
    
    @property
    def conversations(self) -> AsyncConversations:
        """Access to conversation management."""
        return self._conversations
        
    @property
    def mcp(self) -> AsyncMCPClient:
        """Access to the MCP (Machine Control Protocol) client.
        
        The MCP client allows you to interact with the TNSA MCP server to discover
        and call various tools and services asynchronously.
        
        Example:
            # List available tools
            tools = await client.mcp.list_tools()
            
            # Call a tool
            result = await client.mcp.call_tool("tool_name", {"param": "value"})
            
        Returns:
            AsyncMCPClient: An instance of the async MCP client
        """
        if self._mcp_client is None:
            # Lazy initialization of MCP client
            mcp_url = self.config.base_url.replace('api', 'mcp', 1)  # Convert api. to mcp.
            self._mcp_client = AsyncMCPClient(
                server_url=mcp_url,
                api_key=self.config.api_key
            )
        return self._mcp_client
    
    async def aclose(self):
        """Close the client and cleanup resources."""
        if hasattr(self, '_http_client') and self._http_client:
            await self._http_client.aclose()
            
        # Close MCP client if it was initialized
        if hasattr(self, '_mcp_client') and self._mcp_client is not None:
            await self._mcp_client.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.aclose())
            else:
                loop.run_until_complete(self.aclose())
        except:
            pass  # Ignore errors during cleanup