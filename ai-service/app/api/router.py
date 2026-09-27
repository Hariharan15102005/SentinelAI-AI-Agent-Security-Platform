import re
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, status

from app.models.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    HealthResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentListResponse,
    DocumentDetailResponse,
    DocumentSummaryResponse,
    DocumentChunkModel,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGHealthResponse
)
from app.core.auth import verify_internal_token
from app.services.runner import runner_service
from app.config.settings import settings
from app.rag.chroma_service import default_chroma_service
from app.rag.rag_pipeline import default_rag_pipeline
from app.crew import (
    CrewAssessmentRequest,
    CrewAssessmentReport,
    default_crew_service
)

api_router = APIRouter(prefix="/api/v1")

def parse_trace_id(traceparent: Optional[str], x_trace_id: Optional[str]) -> Optional[str]:
    """Extracts 32-hex trace ID from W3C traceparent or X-Trace-Id header."""
    if traceparent:
        parts = traceparent.split("-")
        if len(parts) >= 2 and len(parts[1]) == 32:
            return parts[1]
    if x_trace_id:
        clean_id = re.sub(r"[^a-fA-F0-9]", "", x_trace_id)
        if len(clean_id) >= 16:
            return clean_id[:32]
    return None

@api_router.post(
    "/agent/run",
    response_model=AgentRunResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="Execute LangGraph Agent Run",
    description="Executes a controlled test run against the LangGraph agent in BASELINE or SECURED mode."
)
async def run_agent(
    request: AgentRunRequest,
    traceparent: Optional[str] = Header(None),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-Id")
) -> AgentRunResponse:
    try:
        incoming_trace_id = parse_trace_id(traceparent, x_trace_id)
        response = runner_service.execute(request, trace_id=incoming_trace_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution encountered an error: {str(e)}"
        )

# ==================== RAG & ChromaDB Endpoints ====================

@api_router.post(
    "/rag/documents",
    response_model=DocumentIngestResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="Ingest Document into ChromaDB",
    description="Chunks, embeds, and stores a document in the ChromaDB vector database."
)
async def ingest_document(request: DocumentIngestRequest) -> DocumentIngestResponse:
    try:
        result = default_chroma_service.ingest_document(
            title=request.title,
            content=request.content,
            document_id=request.documentId,
            filename=request.filename or "document.txt",
            metadata=request.metadata,
            chunk_size=request.chunkSize,
            chunk_overlap=request.chunkOverlap
        )
        return DocumentIngestResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion failed: {str(e)}")

@api_router.get(
    "/rag/documents",
    response_model=DocumentListResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="List Indexed RAG Documents"
)
async def list_documents() -> DocumentListResponse:
    try:
        docs = default_chroma_service.list_documents()
        doc_summaries = [
            DocumentSummaryResponse(
                documentId=d["documentId"],
                title=d["title"],
                filename=d["filename"],
                chunkCount=d["chunkCount"],
                characterCount=d["characterCount"],
                metadata=d.get("metadata", {}),
                createdAt=d.get("createdAt")
            )
            for d in docs
        ]
        total_chunks = sum(d.chunkCount for d in doc_summaries)
        return DocumentListResponse(
            totalDocuments=len(doc_summaries),
            totalChunks=total_chunks,
            documents=doc_summaries
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list documents: {str(e)}")

@api_router.get(
    "/rag/documents/{document_id}",
    response_model=DocumentDetailResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="Get Document Details and Chunks"
)
async def get_document_details(document_id: str) -> DocumentDetailResponse:
    doc = default_chroma_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{document_id}' not found.")
    
    chunks = [
        DocumentChunkModel(
            chunkId=c["chunkId"],
            documentId=c["documentId"],
            chunkIndex=c["chunkIndex"],
            totalChunks=c["totalChunks"],
            content=c["content"],
            metadata=c["metadata"]
        )
        for c in doc["chunks"]
    ]
    return DocumentDetailResponse(
        documentId=doc["documentId"],
        title=doc["title"],
        filename=doc["filename"],
        chunkCount=doc["chunkCount"],
        chunks=chunks
    )

@api_router.delete(
    "/rag/documents/{document_id}",
    dependencies=[Depends(verify_internal_token)],
    summary="Delete Document from ChromaDB"
)
async def delete_document(document_id: str):
    success = default_chroma_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{document_id}' not found.")
    return {"success": True, "documentId": document_id, "message": "Document and all associated chunks deleted."}

@api_router.post(
    "/rag/query",
    response_model=RAGQueryResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="Query RAG Knowledge Base",
    description="Performs semantic search against ChromaDB and generates grounded AI response with citations."
)
async def query_rag(request: RAGQueryRequest) -> RAGQueryResponse:
    try:
        response = default_rag_pipeline.query(
            query_text=request.query,
            top_k=request.topK or 3,
            metadata_filter=request.metadataFilter,
            similarity_threshold=request.similarityThreshold,
            temperature=request.temperature or 0.2,
            system_prompt=request.systemPrompt
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"RAG query error: {str(e)}")

@api_router.get(
    "/rag/health",
    response_model=RAGHealthResponse,
    summary="RAG and ChromaDB Vector Store Health"
)
async def rag_health() -> RAGHealthResponse:
    health = default_chroma_service.get_health()
    return RAGHealthResponse(**health)

# ==================== Model Context Protocol (MCP) Endpoints ====================

from app.mcp.types import (
    JSONRPCRequest,
    JSONRPCResponse,
    MCPToolCallRequest,
    MCPToolCallResponse,
    MCPHealthResponse
)
from app.mcp.server import default_mcp_server
from app.mcp.client import default_mcp_client

@api_router.post(
    "/mcp/rpc",
    dependencies=[Depends(verify_internal_token)],
    summary="MCP JSON-RPC 2.0 Protocol Gateway",
    description="Standard JSON-RPC 2.0 entry point for external MCP clients and AI agent tools."
)
async def mcp_rpc(request: Dict[str, Any]) -> Dict[str, Any]:
    return default_mcp_server.handle_jsonrpc(request)

@api_router.get(
    "/mcp/tools",
    dependencies=[Depends(verify_internal_token)],
    summary="List Approved MCP Tools",
    description="Returns available MCP tools with their JSONSchema input definitions."
)
async def list_mcp_tools() -> Dict[str, Any]:
    tools = default_mcp_client.list_tools()
    return {"tools": [t.model_dump() for t in tools]}

@api_router.post(
    "/mcp/tools/call",
    response_model=MCPToolCallResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="Execute Approved MCP Tool",
    description="Invokes an authorized MCP tool with argument validation and authorization checks."
)
async def call_mcp_tool(request: MCPToolCallRequest) -> MCPToolCallResponse:
    response = default_mcp_client.call_tool(name=request.name, arguments=request.arguments)
    return response

@api_router.get(
    "/mcp/resources",
    dependencies=[Depends(verify_internal_token)],
    summary="List Available MCP Resources",
    description="Returns all registered resource URIs and metadata."
)
async def list_mcp_resources() -> Dict[str, Any]:
    resources = default_mcp_client.list_resources()
    return {"resources": [r.model_dump() for r in resources]}

@api_router.get(
    "/mcp/resources/read",
    dependencies=[Depends(verify_internal_token)],
    summary="Read MCP Resource",
    description="Reads the text content of a registered MCP resource by URI."
)
async def read_mcp_resource(uri: str) -> Dict[str, Any]:
    try:
        content = default_mcp_client.read_resource(uri)
        return content
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to read resource: {str(e)}")

@api_router.get(
    "/mcp/health",
    response_model=MCPHealthResponse,
    summary="MCP Server and Client Health Check"
)
async def mcp_health() -> MCPHealthResponse:
    health = default_mcp_client.get_health()
    return health

# ==================== Centralized LLM Gateway Endpoints ====================

from app.gateway.types import (
    GatewayGenerateRequest,
    GatewayGenerateResponse,
    GatewayModelsResponse,
    GatewayUsageMetrics,
    GatewayHealthResponse
)
from app.gateway.llm_gateway import default_llm_gateway
from app.gateway.usage_tracker import default_usage_tracker

@api_router.post(
    "/gateway/generate",
    response_model=GatewayGenerateResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="Centralized LLM Gateway Generation",
    description="Validates, rate-limits, routes, and tracks token usage for LLM completions."
)
async def gateway_generate(request: GatewayGenerateRequest) -> GatewayGenerateResponse:
    try:
        response = default_llm_gateway.generate(request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gateway Generation Error: {str(e)}")

@api_router.get(
    "/gateway/models",
    response_model=GatewayModelsResponse,
    dependencies=[Depends(verify_internal_token)],
    summary="List Gateway Providers and Models",
    description="Returns registered LLM providers and available model catalogs."
)
async def get_gateway_models() -> GatewayModelsResponse:
    return default_llm_gateway.list_available_models()

@api_router.get(
    "/gateway/usage",
    response_model=GatewayUsageMetrics,
    dependencies=[Depends(verify_internal_token)],
    summary="Get Gateway Token Usage and Cost Metrics",
    description="Aggregated token counts, successful/failed requests, and estimated USD expenditure."
)
async def get_gateway_usage() -> GatewayUsageMetrics:
    return default_usage_tracker.get_metrics()

@api_router.get(
    "/gateway/health",
    response_model=GatewayHealthResponse,
    summary="LLM Gateway Health and Active Providers"
)
async def gateway_health() -> GatewayHealthResponse:
    return default_llm_gateway.get_health()

# ==================== CrewAI Multi-Agent Security Assessment Endpoints ====================

@api_router.post(
    "/crew/assess",
    response_model=CrewAssessmentReport,
    dependencies=[Depends(verify_internal_token)],
    summary="Execute Multi-Agent AI Security Assessment",
    description="Orchestrates Security Analyst, Security Tester, and Security Reporter agents to evaluate target AI security."
)
async def execute_crew_assessment(request: CrewAssessmentRequest) -> CrewAssessmentReport:
    try:
        report = default_crew_service.execute_assessment(request)
        return report
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CrewAI Assessment Workflow Error: {str(e)}"
        )

@api_router.get(
    "/crew/reports",
    dependencies=[Depends(verify_internal_token)],
    summary="List Completed Security Assessment Reports",
    description="Returns high-level summaries of all multi-agent security assessments performed."
)
async def list_crew_reports() -> Dict[str, Any]:
    summaries = default_crew_service.list_reports()
    return {"total": len(summaries), "reports": summaries}

@api_router.get(
    "/crew/reports/{assessment_id}",
    response_model=CrewAssessmentReport,
    dependencies=[Depends(verify_internal_token)],
    summary="Get Detailed Security Assessment Report",
    description="Retrieves a complete CrewAI assessment report by its unique assessment ID."
)
async def get_crew_report(assessment_id: str) -> CrewAssessmentReport:
    report = default_crew_service.get_report(assessment_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security assessment report '{assessment_id}' not found."
        )
    return report

@api_router.get(
    "/health",
    response_model=HealthResponse,
    summary="AI Microservice Health Check"
)
async def health_check() -> HealthResponse:
    gemini_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here")
    return HealthResponse(
        status="HEALTHY",
        version="1.0.0",
        geminiApiConfigured=gemini_configured,
        mockModeActive=not gemini_configured or settings.MOCK_LLM_MODE
    )




