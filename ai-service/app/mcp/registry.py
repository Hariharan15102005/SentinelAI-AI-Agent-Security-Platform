import json
from typing import Dict, Any, List, Optional
from app.mcp.types import (
    MCPToolDefinition,
    ToolInputSchema,
    MCPResourceDefinition,
    MCPResourceContent
)

# ==================== Tool Definitions ====================

SENTINELAI_MCP_TOOLS: Dict[str, MCPToolDefinition] = {
    "sentinelai_rag_search": MCPToolDefinition(
        name="sentinelai_rag_search",
        description="Search the SentinelAI ChromaDB knowledge repository for verified policy, architecture, and documentation excerpts.",
        inputSchema=ToolInputSchema(
            type="object",
            properties={
                "query": {
                    "type": "string",
                    "description": "Semantic search query to locate relevant context in the knowledge base"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Maximum number of matching chunks to retrieve (1-10)",
                    "default": 3
                },
                "similarity_threshold": {
                    "type": "number",
                    "description": "Minimum cosine similarity score threshold (0.0 - 1.0)",
                    "default": 0.35
                }
            },
            required=["query"]
        )
    ),
    "sentinelai_list_documents": MCPToolDefinition(
        name="sentinelai_list_documents",
        description="List all indexed documents, titles, filenames, and chunk counts stored in the SentinelAI vector database.",
        inputSchema=ToolInputSchema(
            type="object",
            properties={},
            required=[]
        )
    ),
    "sentinelai_evaluate_security": MCPToolDefinition(
        name="sentinelai_evaluate_security",
        description="Run the SentinelAI Guardrails engine on input text to scan for prompt injections, jailbreaks, and PII leakage.",
        inputSchema=ToolInputSchema(
            type="object",
            properties={
                "text": {
                    "type": "string",
                    "description": "Input text or prompt to scan against security guardrails"
                }
            },
            required=["text"]
        )
    ),
    "sentinelai_calculate": MCPToolDefinition(
        name="sentinelai_calculate",
        description="Perform safe mathematical evaluation using an isolated Abstract Syntax Tree (AST) evaluator.",
        inputSchema=ToolInputSchema(
            type="object",
            properties={
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to safely calculate (e.g. '1299.99 * 0.15')"
                }
            },
            required=["expression"]
        )
    ),
    "sentinelai_db_lookup": MCPToolDefinition(
        name="sentinelai_db_lookup",
        description="Lookup customer order details and status from the sandboxed database with SQL injection protection.",
        inputSchema=ToolInputSchema(
            type="object",
            properties={
                "query_type": {
                    "type": "string",
                    "description": "Target entity table ('orders' or 'customers')",
                    "default": "orders"
                },
                "query_param": {
                    "type": "string",
                    "description": "Identifier key to search (e.g. '1001', '1002')"
                }
            },
            required=["query_param"]
        )
    )
}

# ==================== Resource Definitions ====================

SENTINELAI_MCP_RESOURCES: Dict[str, MCPResourceDefinition] = {
    "sentinelai://policies/return_policy": MCPResourceDefinition(
        uri="sentinelai://policies/return_policy",
        name="TechCorp Return and Refund Policy",
        description="Official 30-day customer return and refund terms and warranty guidelines.",
        mimeType="text/markdown"
    ),
    "sentinelai://policies/security_standard": MCPResourceDefinition(
        uri="sentinelai://policies/security_standard",
        name="SentinelAI Security Guidelines",
        description="Security standard covering PII masking, RBAC, and guardrails enforcement.",
        mimeType="text/markdown"
    ),
    "sentinelai://system/metrics": MCPResourceDefinition(
        uri="sentinelai://system/metrics",
        name="Platform Metrics Summary",
        description="Runtime system telemetry, active guardrails, and knowledge base statistics.",
        mimeType="application/json"
    )
}

# ==================== Permissions & Authorization Matrix ====================

APPROVED_MCP_TOOLS: set = {
    "sentinelai_rag_search",
    "sentinelai_list_documents",
    "sentinelai_evaluate_security",
    "sentinelai_calculate",
    "sentinelai_db_lookup"
}

TOOL_PERMISSIONS: Dict[str, str] = {
    "sentinelai_rag_search": "rag:read",
    "sentinelai_list_documents": "rag:read",
    "sentinelai_evaluate_security": "security:eval",
    "sentinelai_calculate": "tool:math",
    "sentinelai_db_lookup": "tool:db"
}

def is_tool_authorized(tool_name: str, granted_scopes: Optional[List[str]] = None) -> bool:
    """Verifies that a tool is explicitly in the approved allowlist and has required permission scopes."""
    if tool_name not in APPROVED_MCP_TOOLS:
        return False
    if not granted_scopes:
        return True  # Internal default service scope
    required_scope = TOOL_PERMISSIONS.get(tool_name)
    return required_scope is None or required_scope in granted_scopes or "admin" in granted_scopes
