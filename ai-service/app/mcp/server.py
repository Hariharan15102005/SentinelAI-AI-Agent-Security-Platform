import time
import json
import logging
from typing import Dict, Any, List, Optional

from app.config.settings import settings
from app.mcp.types import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    MCPToolDefinition,
    MCPResourceDefinition,
    MCPToolCallResult,
    MCPContentItem,
    MCPResourceContent
)
from app.mcp.registry import (
    SENTINELAI_MCP_TOOLS,
    SENTINELAI_MCP_RESOURCES,
    APPROVED_MCP_TOOLS,
    is_tool_authorized
)
from app.agent.tools import (
    tool_calculator,
    tool_mock_database_lookup,
    tool_controlled_doc_search,
    MOCK_DOCUMENTS
)
from app.guardrails.engine import GuardrailsEngine
from app.rag.chroma_service import default_chroma_service

logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(
        self,
        server_name: Optional[str] = None,
        server_version: Optional[str] = None,
        protocol_version: Optional[str] = None
    ):
        self.server_name = server_name or settings.MCP_SERVER_NAME
        self.server_version = server_version or settings.MCP_SERVER_VERSION
        self.protocol_version = protocol_version or settings.MCP_PROTOCOL_VERSION
        self.guardrails_engine = GuardrailsEngine()
        self._initialized = False

    def handle_jsonrpc(self, request: Dict[str, Any], caller_scopes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches incoming JSON-RPC 2.0 protocol request to appropriate handler."""
        try:
            req = JSONRPCRequest(**request)
        except Exception as e:
            return JSONRPCResponse(
                id=request.get("id", None),
                error=JSONRPCError(code=-32600, message=f"Invalid JSON-RPC 2.0 Request: {str(e)}")
            ).model_dump()

        method = req.method
        params = req.params or {}

        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                result = self._handle_tools_call(params, caller_scopes)
            elif method == "resources/list":
                result = self._handle_resources_list()
            elif method == "resources/read":
                result = self._handle_resources_read(params)
            else:
                return JSONRPCResponse(
                    id=req.id,
                    error=JSONRPCError(code=-32601, message=f"Method '{method}' not found or unsupported by MCP server.")
                ).model_dump()

            return JSONRPCResponse(id=req.id, result=result).model_dump()
        except ValueError as ve:
            return JSONRPCResponse(
                id=req.id,
                error=JSONRPCError(code=-32602, message=f"Invalid parameter: {str(ve)}")
            ).model_dump()
        except PermissionError as pe:
            return JSONRPCResponse(
                id=req.id,
                error=JSONRPCError(code=-32001, message=f"MCP Authorization Denied: {str(pe)}")
            ).model_dump()
        except Exception as e:
            logger.error(f"MCP Internal Error on method '{method}': {str(e)}")
            return JSONRPCResponse(
                id=req.id,
                error=JSONRPCError(code=-32002, message=f"Tool Execution Error: {str(e)}")
            ).model_dump()

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._initialized = True
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "logging": {}
            },
            "serverInfo": {
                "name": self.server_name,
                "version": self.server_version
            }
        }

    def _handle_tools_list(self) -> Dict[str, Any]:
        tools = [tool.model_dump() for tool in SENTINELAI_MCP_TOOLS.values()]
        return {"tools": tools}

    def _handle_resources_list(self) -> Dict[str, Any]:
        resources = [res.model_dump() for res in SENTINELAI_MCP_RESOURCES.values()]
        return {"resources": resources}

    def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        uri = params.get("uri")
        if not uri:
            raise ValueError("Parameter 'uri' is required for resources/read.")

        if uri == "sentinelai://policies/return_policy":
            content = MOCK_DOCUMENTS.get("return_policy", "TechCorp Return Policy v3.2: 30 days full refund.")
            return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": content}]}
        elif uri == "sentinelai://policies/security_standard":
            content = MOCK_DOCUMENTS.get("privacy_policy", "Customer PII must never be emitted in plain text.")
            return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": content}]}
        elif uri == "sentinelai://system/metrics":
            health = default_chroma_service.get_health()
            return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(health, indent=2)}]}
        else:
            raise ValueError(f"Resource URI '{uri}' not found in registered MCP resources.")

    def _handle_tools_call(self, params: Dict[str, Any], caller_scopes: Optional[List[str]] = None) -> Dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments", {})

        if not name:
            raise ValueError("Tool name is required in tools/call.")

        # 1. Authorization & Allowlist Check
        if not is_tool_authorized(name, caller_scopes):
            raise PermissionError(f"Tool '{name}' is not in the approved MCP tool list or caller lacks required scopes.")

        tool_def = SENTINELAI_MCP_TOOLS.get(name)
        if not tool_def:
            raise ValueError(f"Unknown tool: '{name}'.")

        # 2. Input Schema & Parameter Validation
        required_fields = tool_def.inputSchema.required or []
        for field in required_fields:
            if field not in arguments:
                raise ValueError(f"Missing required argument '{field}' for tool '{name}'.")

        # 3. Dispatch to Concrete Tool Implementation
        start_time = time.time()
        tool_output_text = ""
        is_error = False

        if name == "sentinelai_rag_search":
            query = str(arguments.get("query", "")).strip()
            if len(query) > 1000:
                raise ValueError("Query string exceeds maximum limit of 1000 characters.")
            top_k = int(arguments.get("top_k", 3))
            threshold = float(arguments.get("similarity_threshold", 0.35))
            
            hits = default_chroma_service.query(
                query_text=query,
                top_k=min(top_k, 10),
                similarity_threshold=threshold
            )
            if hits:
                formatted_hits = []
                for h in hits:
                    formatted_hits.append(
                        f"• [{h['title']}] (Score: {h['similarityScore']})\n  {h['content']}"
                    )
                tool_output_text = "\n\n".join(formatted_hits)
            else:
                tool_output_text = "No matching knowledge base documents found above the similarity threshold."

        elif name == "sentinelai_list_documents":
            docs = default_chroma_service.list_documents()
            summary_list = [
                f"- Document: '{d['title']}' (ID: {d['documentId']}, Chunks: {d['chunkCount']}, File: {d['filename']})"
                for d in docs
            ]
            tool_output_text = f"Total Indexed Documents: {len(docs)}\n" + "\n".join(summary_list)

        elif name == "sentinelai_evaluate_security":
            target_text = str(arguments.get("text", "")).strip()
            if not target_text:
                raise ValueError("Target text to evaluate cannot be empty.")
            guard_findings, should_block, sanitized = self.guardrails_engine.scan_input(target_text)
            
            summary = {
                "blocked": should_block,
                "sanitized": sanitized != target_text,
                "findingsCount": len(guard_findings),
                "findings": [
                    {
                        "rule": f.rule_name,
                        "threat": f.threat_type,
                        "severity": f.severity,
                        "action": f.action_taken
                    }
                    for f in guard_findings
                ]
            }
            tool_output_text = json.dumps(summary, indent=2)

        elif name == "sentinelai_calculate":
            expr = str(arguments.get("expression", "")).strip()
            calc_res = tool_calculator(expr)
            if calc_res.get("success"):
                tool_output_text = f"Result: {calc_res.get('result')}"
            else:
                tool_output_text = f"Calculation Error: {calc_res.get('error')}"
                is_error = True

        elif name == "sentinelai_db_lookup":
            q_type = str(arguments.get("query_type", "orders")).strip()
            q_param = str(arguments.get("query_param", "")).strip()
            db_res = tool_mock_database_lookup(q_type, q_param, is_secured=True)
            if db_res.get("success"):
                tool_output_text = json.dumps(db_res.get("record", {}), indent=2)
            else:
                tool_output_text = f"Database Lookup Notice: {db_res.get('error', 'Record not found')}"
                if db_res.get("blocked"):
                    is_error = True

        duration_ms = int((time.time() - start_time) * 1000)

        return MCPToolCallResult(
            content=[MCPContentItem(type="text", text=tool_output_text)],
            isError=is_error,
            metadata={
                "tool": name,
                "durationMs": duration_ms,
                "timestamp": int(time.time() * 1000)
            }
        ).model_dump()

default_mcp_server = MCPServer()
