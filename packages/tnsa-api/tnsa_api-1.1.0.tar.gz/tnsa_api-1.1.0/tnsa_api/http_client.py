"""
HTTP client with retry logic and error handling for TNSA API.
"""

import time
import random
import json
import asyncio
import requests
import aiohttp
from typing import Dict, Any, Optional, Union, Iterator, AsyncIterator
from urllib.parse import urljoin

from .config import Config
from .exceptions import (
    TNSAError,
    APIConnectionError,
    APITimeoutError,
    create_error_from_response,
)


def clean_response_content(content: str) -> str:
    """Clean response content by removing <think> tags."""
    if "<think>" in content and "</think>" in content:
        # Extract content after </think>
        think_end = content.find("</think>")
        if think_end != -1:
            return content[think_end + 8:].strip()
    return content


class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to avoid thundering herd
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def should_retry(self, attempt: int, status_code: Optional[int] = None) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.max_retries:
            return False
        
        if status_code is None:
            # Network error - retry
            return True
        
        # Retry on server errors and rate limits
        if status_code >= 500 or status_code == 429:
            return True
        
        # Don't retry client errors (except rate limit)
        return False


class HTTPClient:
    """Synchronous HTTP client with retry logic."""
    
    def __init__(self, config: Config):
        self.config = config
        self.retry_config = RetryConfig(max_retries=config.max_retries)
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update(config.get_headers())
        
        # Configure session
        self.session.timeout = config.timeout
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
    ) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = urljoin(self.config.base_url, endpoint.lstrip('/'))
        
        # Merge headers
        request_headers = self.config.get_headers()
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    stream=stream,
                    timeout=self.config.timeout,
                )
                
                # Check if we should retry based on status code
                if not self.retry_config.should_retry(attempt, response.status_code):
                    return response
                
                # If we should retry, wait before next attempt
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.calculate_delay(attempt)
                    time.sleep(delay)
                    continue
                
                return response
                
            except requests.exceptions.Timeout as e:
                last_exception = APITimeoutError(
                    f"Request timed out after {self.config.timeout}s",
                    timeout=self.config.timeout
                )
            except requests.exceptions.ConnectionError as e:
                last_exception = APIConnectionError(f"Connection failed: {e}")
            except requests.exceptions.RequestException as e:
                last_exception = TNSAError(f"Request failed: {e}")
            
            # If this was the last attempt, raise the exception
            if attempt >= self.retry_config.max_retries:
                break
            
            # Wait before retry
            delay = self.retry_config.calculate_delay(attempt)
            time.sleep(delay)
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise TNSAError("Request failed after all retries")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        response = self._make_request("GET", endpoint, params=params)
        return self._handle_response(response)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Make POST request."""
        response = self._make_request("POST", endpoint, data=data, stream=stream)
        
        if stream:
            return self._handle_streaming_response(response)
        else:
            return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle non-streaming response."""
        if response.status_code >= 400:
            self._raise_for_status(response)
        
        # TNSA API always returns streaming data, so we need to parse it
        try:
            # Check if it's streaming format
            response_text = response.text.strip()
            if response_text.startswith("data: "):
                # Parse streaming response and get the final result
                full_response = ""
                stats = {}
                
                for line in response_text.split('\n'):
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "token" in data:
                                full_response += data["token"]
                            elif "stats" in data:
                                stats = data["stats"]
                            elif "full_response" in data:
                                # Use the full_response if available
                                full_response = data["full_response"]
                                stats = data.get("stats", {})
                        except json.JSONDecodeError:
                            continue
                
                # Clean the response content
                full_response = clean_response_content(full_response)
                
                # Return in TNSA API format
                return {
                    "response": full_response,
                    "chat_id": "chatcmpl-" + str(int(time.time())),
                    "prompt_tokens": stats.get("prompt_tokens", 0),
                    "completion_tokens": stats.get("completion_tokens", 0),
                    "cost": stats.get("cost", 0.0),
                    "latency": stats.get("latency", 0.0)
                }
            else:
                # Try regular JSON parsing
                return response.json()
        except json.JSONDecodeError:
            raise TNSAError(f"Invalid JSON response: {response.text}")
    
    def _handle_streaming_response(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """Handle streaming response."""
        if response.status_code >= 400:
            self._raise_for_status(response)
        
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            raise TNSAError(f"Streaming error: {e}")
    
    def _raise_for_status(self, response: requests.Response):
        """Raise appropriate exception for HTTP error status."""
        try:
            error_data = response.json()
        except json.JSONDecodeError:
            error_data = {"error": {"message": response.text or "Unknown error"}}
        
        request_id = response.headers.get("x-request-id")
        raise create_error_from_response(response.status_code, error_data, request_id)


class AsyncHTTPClient:
    """Asynchronous HTTP client with retry logic."""
    
    def __init__(self, config: Config):
        self.config = config
        self.retry_config = RetryConfig(max_retries=config.max_retries)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                headers=self.config.get_headers(),
                timeout=timeout,
            )
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> aiohttp.ClientResponse:
        """Make HTTP request with retry logic."""
        await self._ensure_session()
        url = urljoin(self.config.base_url, endpoint.lstrip('/'))
        
        # Merge headers
        request_headers = self.config.get_headers()
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                ) as response:
                    # For successful responses or non-retryable errors, return immediately
                    if not self.retry_config.should_retry(attempt, response.status):
                        # Read the response content before returning
                        content = await response.read()
                        # Create a new response-like object with the content
                        return ResponseWrapper(response, content)
                    
                    # If we should retry, continue to next iteration
                    if attempt < self.retry_config.max_retries:
                        delay = self.retry_config.calculate_delay(attempt)
                        await asyncio.sleep(delay)
                        continue
                    
                    # Last attempt - return the response
                    content = await response.read()
                    return ResponseWrapper(response, content)
                    
            except aiohttp.ClientTimeout as e:
                last_exception = APITimeoutError(
                    f"Request timed out after {self.config.timeout}s",
                    timeout=self.config.timeout
                )
            except aiohttp.ClientConnectionError as e:
                last_exception = APIConnectionError(f"Connection failed: {e}")
            except aiohttp.ClientError as e:
                last_exception = TNSAError(f"Request failed: {e}")
            
            # If this was the last attempt, raise the exception
            if attempt >= self.retry_config.max_retries:
                break
            
            # Wait before retry
            delay = self.retry_config.calculate_delay(attempt)
            await asyncio.sleep(delay)
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise TNSAError("Request failed after all retries")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        response = await self._make_request("GET", endpoint, params=params)
        return await self._handle_response(response)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """Make POST request."""
        if stream:
            return self._handle_streaming_request(endpoint, data)
        else:
            response = await self._make_request("POST", endpoint, data=data)
            return await self._handle_response(response)
    
    async def _handle_response(self, response) -> Dict[str, Any]:
        """Handle non-streaming response."""
        if response.status >= 400:
            await self._raise_for_status(response)
        
        # TNSA API always returns streaming data, so we need to parse it
        try:
            text = response.content.decode('utf-8').strip()
            if text.startswith("data: "):
                # Parse streaming response and get the final result
                full_response = ""
                stats = {}
                
                for line in text.split('\n'):
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "token" in data:
                                full_response += data["token"]
                            elif "stats" in data:
                                stats = data["stats"]
                            elif "full_response" in data:
                                # Use the full_response if available
                                full_response = data["full_response"]
                                stats = data.get("stats", {})
                        except json.JSONDecodeError:
                            continue
                
                # Clean the response content
                full_response = clean_response_content(full_response)
                
                # Return in TNSA API format
                return {
                    "response": full_response,
                    "chat_id": "chatcmpl-" + str(int(time.time())),
                    "prompt_tokens": stats.get("prompt_tokens", 0),
                    "completion_tokens": stats.get("completion_tokens", 0),
                    "cost": stats.get("cost", 0.0),
                    "latency": stats.get("latency", 0.0)
                }
            else:
                # Try regular JSON parsing
                return json.loads(text)
        except json.JSONDecodeError:
            raise TNSAError(f"Invalid JSON response: {text}")
    
    async def _handle_streaming_request(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle streaming request."""
        await self._ensure_session()
        url = urljoin(self.config.base_url, endpoint.lstrip('/'))
        
        async with self._session.post(
            url,
            json=data,
            headers=self.config.get_headers(),
        ) as response:
            if response.status >= 400:
                content = await response.read()
                wrapper = ResponseWrapper(response, content)
                await self._raise_for_status(wrapper)
            
            async for line in response.content:
                line_str = line.decode('utf-8').strip()
                if line_str and line_str.startswith("data: "):
                    data_str = line_str[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
    
    async def _raise_for_status(self, response):
        """Raise appropriate exception for HTTP error status."""
        try:
            text = response.content.decode('utf-8')
            error_data = json.loads(text)
        except json.JSONDecodeError:
            error_data = {"error": {"message": text or "Unknown error"}}
        
        request_id = response.headers.get("x-request-id")
        raise create_error_from_response(response.status, error_data, request_id)


class ResponseWrapper:
    """Wrapper for aiohttp response to make it compatible with sync interface."""
    
    def __init__(self, response: aiohttp.ClientResponse, content: bytes):
        self.status = response.status
        self.headers = response.headers
        self.content = content