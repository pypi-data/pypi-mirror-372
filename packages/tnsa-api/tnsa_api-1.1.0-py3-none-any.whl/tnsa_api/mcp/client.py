"""
MCP Client implementation for the TNSA SDK.

This module provides a client for interacting with the TNSA MCP server,
enabling integration with various tools and services.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union

from fastmcp import Client as FastMCPClient
from fastmcp.client.transports import StreamableHttpTransport

from ..exceptions import TNSAError


class MCPError(TNSAError):
    """Base exception for MCP client errors."""
    pass


class MCPConnectionError(MCPError):
    """Raised when there is an error connecting to the MCP server."""
    pass


class MCPAuthenticationError(MCPError):
    """Raised when authentication with the MCP server fails."""
    pass


class MCPClient:
    """Client for interacting with the TNSA MCP server.
    
    This client provides methods to list available tools and call them
    on the MCP server.
    """
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        """Initialize the MCP client.
        
        Args:
            server_url: The URL of the MCP server.
            api_key: Optional API key for authentication.
        """
        self.server_url = server_url
        self.api_key = api_key
        self._client = None
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self):
        """Establish a connection to the MCP server."""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            transport = StreamableHttpTransport(
                self.server_url,
                headers=headers
            )
            self._client = FastMCPClient(transport=transport)
            await self._client.__aenter__()
            
            if not await self._client.is_connected():
                raise MCPConnectionError("Failed to connect to MCP server")
                
        except Exception as e:
            raise MCPConnectionError(f"Failed to connect to MCP server: {str(e)}")
    
    async def close(self):
        """Close the connection to the MCP server."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools on the MCP server.
        
        Returns:
            A list of dictionaries containing tool information.
            
        Raises:
            MCPError: If there is an error listing tools.
        """
        if not self._client:
            raise MCPError("Not connected to MCP server. Call connect() first.")
            
        try:
            tools = await self._client.list_tools()
            return [
                {
                    "name": getattr(tool, "name", ""),
                    "description": getattr(tool, "description", ""),
                    "input_schema": getattr(tool, "input_schema", {})
                }
                for tool in tools
            ]
        except Exception as e:
            raise MCPError(f"Failed to list tools: {str(e)}")
    
    async def call_tool(
        self, 
        tool_name: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: The name of the tool to call.
            params: Optional dictionary of parameters to pass to the tool.
            
        Returns:
            The result of the tool call.
            
        Raises:
            MCPError: If there is an error calling the tool.
        """
        if not self._client:
            raise MCPError("Not connected to MCP server. Call connect() first.")
            
        try:
            params = params or {}
            result = await self._client.call_tool(tool_name, params)
            
            # Process the result to make it more user-friendly
            if result and hasattr(result[0], "text") and result[0].text:
                try:
                    return json.loads(result[0].text)
                except json.JSONDecodeError:
                    return result[0].text
            return result
            
        except Exception as e:
            raise MCPError(f"Failed to call tool '{tool_name}': {str(e)}")
    
    async def is_connected(self) -> bool:
        """Check if the client is connected to the MCP server.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        return self._client is not None and await self._client.is_connected()
