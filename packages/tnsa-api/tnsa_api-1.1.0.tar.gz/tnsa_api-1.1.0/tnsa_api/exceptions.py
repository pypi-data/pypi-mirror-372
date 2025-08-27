"""
Exception classes for TNSA API client.
"""

from typing import Optional, Dict, Any


class TNSAError(Exception):
    """Base exception for TNSA API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class AuthenticationError(TNSAError):
    """Authentication failed - invalid API key or unauthorized access."""
    pass


class RateLimitError(TNSAError):
    """Rate limit exceeded - too many requests."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ModelNotFoundError(TNSAError):
    """Requested model is not available."""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        available_models: Optional[list] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.available_models = available_models or []


class InvalidRequestError(TNSAError):
    """Invalid request parameters or malformed request."""
    
    def __init__(
        self,
        message: str,
        param: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.param = param


class APIConnectionError(TNSAError):
    """Connection to API failed - network or server issues."""
    pass


class APITimeoutError(TNSAError):
    """Request timed out."""
    
    def __init__(
        self,
        message: str,
        timeout: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.timeout = timeout


class ServerError(TNSAError):
    """Server-side error (5xx status codes)."""
    pass


class BadRequestError(TNSAError):
    """Bad request error (4xx status codes)."""
    pass


def create_error_from_response(
    status_code: int,
    response_data: Dict[str, Any],
    request_id: Optional[str] = None,
) -> TNSAError:
    """Create appropriate error from HTTP response."""
    
    message = response_data.get("error", {}).get("message", "Unknown error")
    if isinstance(message, dict):
        message = str(message)
    
    error_kwargs = {
        "status_code": status_code,
        "response_data": response_data,
        "request_id": request_id,
    }
    
    if status_code == 401:
        return AuthenticationError(message, **error_kwargs)
    elif status_code == 429:
        retry_after = response_data.get("retry_after")
        return RateLimitError(message, retry_after=retry_after, **error_kwargs)
    elif status_code == 404:
        return ModelNotFoundError(message, **error_kwargs)
    elif status_code == 400:
        param = response_data.get("error", {}).get("param")
        return InvalidRequestError(message, param=param, **error_kwargs)
    elif 400 <= status_code < 500:
        return BadRequestError(message, **error_kwargs)
    elif 500 <= status_code < 600:
        return ServerError(message, **error_kwargs)
    else:
        return TNSAError(message, **error_kwargs)