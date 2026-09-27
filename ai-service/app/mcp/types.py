from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

# ==================== MCP Protocol Types (JSON-RPC 2.0) ====================

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = 1
    method: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)

class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = 1
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None

# ==================== MCP Tool & Resource Types ====================

class ToolInputSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: Optional[List[str]] = Field(default_factory=list)

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: ToolInputSchema

class MCPResourceDefinition(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = "text/plain"

class MCPContentItem(BaseModel):
    type: str = "text"
    text: str

class MCPToolCallResult(BaseModel):
    content: List[MCPContentItem]
    isError: bool = False
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MCPResourceContent(BaseModel):
    uri: str
    mimeType: str = "text/plain"
    text: str

# ==================== MCP Service Level Schemas ====================

class MCPToolCallRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Approved MCP tool name to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments matching tool's input schema")

class MCPToolCallResponse(BaseModel):
    tool: str
    success: bool
    result: Any
    isError: bool = False
    error: Optional[str] = None
    durationMs: int = 0

class MCPHealthResponse(BaseModel):
    status: str = "HEALTHY"
    serverName: str
    serverVersion: str
    protocolVersion: str
    totalTools: int
    totalResources: int
    tools: List[str]
