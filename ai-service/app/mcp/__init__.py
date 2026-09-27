"""SentinelAI Model Context Protocol (MCP) Module"""
from app.mcp.types import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    MCPToolDefinition,
    MCPResourceDefinition,
    MCPToolCallRequest,
    MCPToolCallResponse,
    MCPHealthResponse
)
from app.mcp.registry import (
    SENTINELAI_MCP_TOOLS,
    SENTINELAI_MCP_RESOURCES,
    APPROVED_MCP_TOOLS,
    is_tool_authorized
)
from app.mcp.server import MCPServer, default_mcp_server
from app.mcp.client import MCPClient, default_mcp_client

__all__ = [
    "JSONRPCRequest",
    "JSONRPCResponse",
    "JSONRPCError",
    "MCPToolDefinition",
    "MCPResourceDefinition",
    "MCPToolCallRequest",
    "MCPToolCallResponse",
    "MCPHealthResponse",
    "SENTINELAI_MCP_TOOLS",
    "SENTINELAI_MCP_RESOURCES",
    "APPROVED_MCP_TOOLS",
    "is_tool_authorized",
    "MCPServer",
    "default_mcp_server",
    "MCPClient",
    "default_mcp_client"
]
