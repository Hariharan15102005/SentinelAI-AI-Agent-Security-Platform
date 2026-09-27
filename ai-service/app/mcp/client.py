import time
import uuid
import logging
from typing import Dict, Any, List, Optional

from app.mcp.types import (
    JSONRPCRequest,
    MCPToolDefinition,
    MCPResourceDefinition,
    MCPToolCallResponse,
    MCPHealthResponse
)
from app.mcp.server import MCPServer, default_mcp_server
from app.config.settings import settings

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, server: Optional[MCPServer] = None):
        self.server = server or default_mcp_server
        self._connected = False
        self._server_capabilities: Dict[str, Any] = {}
        self._tools_cache: Dict[str, MCPToolDefinition] = {}
        self._resources_cache: Dict[str, MCPResourceDefinition] = {}

    def connect(self) -> bool:
        """Initializes connection to the MCP server and negotiates protocol capabilities."""
        try:
            init_req = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": settings.MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {}, "resources": {}},
                    "clientInfo": {"name": "SentinelAI-Agent-Client", "version": "1.0.0"}
                }
            }
            resp = self.server.handle_jsonrpc(init_req)
            if "error" in resp and resp["error"]:
                logger.error(f"MCP Connection failed: {resp['error']}")
                self._connected = False
                return False

            self._connected = True
            self._server_capabilities = resp.get("result", {}).get("capabilities", {})
            self._refresh_caches()
            logger.info("MCP Client successfully connected to server.")
            return True
        except Exception as e:
            logger.error(f"MCP Client connection exception: {e}")
            self._connected = False
            return False

    def is_connected(self) -> bool:
        return self._connected

    def _refresh_caches(self):
        """Fetches and caches tool and resource definitions."""
        try:
            tools_res = self.server.handle_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            if "result" in tools_res and "tools" in tools_res["result"]:
                self._tools_cache = {t["name"]: MCPToolDefinition(**t) for t in tools_res["result"]["tools"]}

            res_res = self.server.handle_jsonrpc({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
            if "result" in res_res and "resources" in res_res["result"]:
                self._resources_cache = {r["uri"]: MCPResourceDefinition(**r) for r in res_res["result"]["resources"]}
        except Exception as e:
            logger.warning(f"Failed to refresh MCP cache: {e}")

    def list_tools(self) -> List[MCPToolDefinition]:
        """Discovers and returns all available MCP tools."""
        if not self._connected:
            self.connect()
        return list(self._tools_cache.values())

    def list_resources(self) -> List[MCPResourceDefinition]:
        """Discovers and returns all available MCP resources."""
        if not self._connected:
            self.connect()
        return list(self._resources_cache.values())

    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Reads content of a specific registered resource."""
        if not self._connected:
            self.connect()

        req = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "resources/read",
            "params": {"uri": uri}
        }
        res = self.server.handle_jsonrpc(req)
        if "error" in res and res["error"]:
            raise ValueError(res["error"]["message"])
        return res.get("result", {})

    def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        caller_scopes: Optional[List[str]] = None,
        trace_id: Optional[str] = None
    ) -> MCPToolCallResponse:
        """
        Validates, dispatches, and executes an MCP tool with telemetry span recording.
        """
        if not self._connected:
            self.connect()

        start_time = time.time()
        req = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments}
        }

        resp = self.server.handle_jsonrpc(req, caller_scopes=caller_scopes)
        duration_ms = int((time.time() - start_time) * 1000)

        if "error" in resp and resp["error"]:
            err_msg = resp["error"]["message"]
            return MCPToolCallResponse(
                tool=name,
                success=False,
                result=None,
                isError=True,
                error=err_msg,
                durationMs=duration_ms
            )

        res_data = resp.get("result", {})
        content_items = res_data.get("content", [])
        output_text = "\n".join([item.get("text", "") for item in content_items])

        return MCPToolCallResponse(
            tool=name,
            success=not res_data.get("isError", False),
            result=output_text,
            isError=res_data.get("isError", False),
            error=None if not res_data.get("isError", False) else output_text,
            durationMs=duration_ms
        )

    def get_health(self) -> MCPHealthResponse:
        """Returns MCP client/server health metrics."""
        if not self._connected:
            self.connect()

        tools = self.list_tools()
        resources = self.list_resources()

        return MCPHealthResponse(
            status="HEALTHY" if self._connected else "DEGRADED",
            serverName=self.server.server_name,
            serverVersion=self.server.server_version,
            protocolVersion=self.server.protocol_version,
            totalTools=len(tools),
            totalResources=len(resources),
            tools=[t.name for t in tools]
        )

default_mcp_client = MCPClient()
