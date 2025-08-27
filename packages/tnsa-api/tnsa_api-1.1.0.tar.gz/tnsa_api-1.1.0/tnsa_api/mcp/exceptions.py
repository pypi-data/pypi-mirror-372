"""
Exceptions for the TNSA MCP client.
"""

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


class MCPServerError(MCPError):
    """Raised when the MCP server returns an error."""
    pass


class MCPToolNotFoundError(MCPError):
    """Raised when a requested tool is not found on the MCP server."""
    pass


class MCPInvalidParametersError(MCPError):
    """Raised when invalid parameters are provided to an MCP tool."""
    pass
