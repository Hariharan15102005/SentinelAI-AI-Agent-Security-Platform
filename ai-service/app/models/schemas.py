from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    systemPrompt: Optional[str] = "You are a customer support agent. Answer questions using the order lookup tool."
    model: Optional[str] = "gemini-1.5-flash"
    temperature: Optional[float] = 0.2

class GuardrailsConfig(BaseModel):
    enabled: bool = True
    rules: List[str] = Field(default_factory=lambda: ["PROMPT_INJECTION", "PII_DETECTION", "TOXICITY", "SQL_INJECTION"])

class EvalConfig(BaseModel):
    enabled: bool = True
    metrics: List[str] = Field(default_factory=lambda: ["FAITHFULNESS", "HALLUCINATION", "ANSWER_RELEVANCY"])

class AgentRunRequest(BaseModel):
    runId: Optional[int] = 1
    projectId: Optional[int] = 1
    agentConfig: Optional[AgentConfig] = Field(default_factory=AgentConfig)
    executionMode: str = Field(default="SECURED", description="BASELINE or SECURED")
    guardrailsConfig: Optional[GuardrailsConfig] = Field(default_factory=GuardrailsConfig)
    evalConfig: Optional[EvalConfig] = Field(default_factory=EvalConfig)
    inputPrompt: str = Field(..., min_length=1, description="The test input prompt")
    contextDocuments: Optional[List[str]] = Field(default_factory=list)

class SecurityFindingModel(BaseModel):
    threatType: str
    severity: str
    guardrailRule: str
    flaggedContent: str
    actionTaken: str
    remediationNotes: Optional[str] = None

class EvaluationResultModel(BaseModel):
    metricName: str
    score: float
    threshold: float
    passed: bool
    reasoning: Optional[str] = None
    evaluationModel: Optional[str] = "gemini-1.5-flash"

class TraceSpanModel(BaseModel):
    traceId: str
    spanId: str
    parentSpanId: Optional[str] = None
    nodeName: str
    nodeType: str
    inputState: Optional[Dict[str, Any]] = None
    outputState: Optional[Dict[str, Any]] = None
    durationMs: int
    promptTokens: int = 0
    completionTokens: int = 0
    status: str = "SUCCESS"
    errorDetails: Optional[str] = None

class AgentRunResponse(BaseModel):
    runId: Optional[int] = 1
    status: str = "COMPLETED"
    finalOutput: str
    isVulnerable: bool = False
    totalLatencyMs: int
    totalTokens: int
    securityFindings: List[SecurityFindingModel] = Field(default_factory=list)
    evaluationResults: List[EvaluationResultModel] = Field(default_factory=list)
    traces: List[TraceSpanModel] = Field(default_factory=list)

class HealthResponse(BaseModel):
    status: str = "HEALTHY"
    version: str = "1.0.0"
    geminiApiConfigured: bool
    mockModeActive: bool

# RAG & ChromaDB Models
class DocumentIngestRequest(BaseModel):
    documentId: Optional[str] = None
    title: str = Field(..., min_length=1, description="Document title")
    content: str = Field(..., min_length=1, description="Raw text content of the document")
    filename: Optional[str] = "document.txt"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    chunkSize: Optional[int] = None
    chunkOverlap: Optional[int] = None

class DocumentChunkModel(BaseModel):
    chunkId: str
    documentId: str
    chunkIndex: int
    totalChunks: int
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentIngestResponse(BaseModel):
    success: bool
    documentId: str
    title: str
    chunksCreated: int
    message: str

class DocumentSummaryResponse(BaseModel):
    documentId: str
    title: str
    filename: str
    chunkCount: int
    characterCount: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    createdAt: Optional[str] = None

class DocumentListResponse(BaseModel):
    totalDocuments: int
    totalChunks: int
    documents: List[DocumentSummaryResponse]

class DocumentDetailResponse(BaseModel):
    documentId: str
    title: str
    filename: str
    chunkCount: int
    chunks: List[DocumentChunkModel]

class RAGSourceReference(BaseModel):
    documentId: str
    chunkId: str
    title: str
    filename: str
    similarityScore: float
    excerpt: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query string to retrieve context for")
    topK: Optional[int] = 3
    metadataFilter: Optional[Dict[str, Any]] = None
    similarityThreshold: Optional[float] = None
    temperature: Optional[float] = 0.2
    systemPrompt: Optional[str] = None

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[RAGSourceReference] = Field(default_factory=list)
    grounded: bool = True
    sufficientContext: bool = True
    latencyMs: int = 0
    tokensUsed: int = 0

class RAGHealthResponse(BaseModel):
    status: str
    collectionName: str
    persistDirectory: str
    totalDocuments: int
    totalChunks: int
    embeddingModel: str
    mode: str

# ==================== AgentDojo Benchmark Schemas ====================

class AgentDojoSuiteInfo(BaseModel):
    id: str
    name: str
    description: str
    tools: List[str]
    environment: str
    userTaskCount: int
    injectionTaskCount: int
    version: str = "v1.0"

class AgentDojoScenarioInfo(BaseModel):
    id: str
    suite: str
    name: str
    category: str = "SECURITY_AGENTDOJO_INDIRECT_INJECTION"
    user_task_id: str
    user_task_prompt: str
    injection_task_id: str
    injection_task_goal: str
    attack_type: str
    attack_payload: str
    severity: str = "HIGH"

class AgentDojoBenchmarkVerdict(BaseModel):
    userTaskCompleted: bool
    attackSuccessful: bool
    agentdojoNativeDefense: str
    attackObjective: str

class SentinelAIVerdict(BaseModel):
    guardrailsActive: bool
    blocked: bool
    threatDetected: bool
    findingsCount: int
    containmentRate: float

class AgentDojoToolTrace(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    raw_output: str
    latency_ms: int
    guardrail_status: str

class AgentDojoRunRequest(BaseModel):
    scenarioId: str = Field(..., description="ID of the canonical or benchmark scenario to execute")
    executionMode: str = Field(default="SECURED", description="BASELINE or SECURED")
    guardrails: Optional[List[str]] = Field(default_factory=lambda: ["PromptInjectionDetector", "PIIAnonymizer", "SQLInjectionGuard"])
    modelName: Optional[str] = "gemini-1.5-flash"

class AgentDojoRunResponse(BaseModel):
    runId: str
    scenarioId: str
    scenarioName: str
    suite: str
    category: str
    userTaskPrompt: str
    injectionTaskGoal: str
    attackType: str
    executionMode: str
    guardrailsApplied: List[str]
    modelName: str
    traceId: str
    latencyMs: int
    status: str = "COMPLETED"
    finalOutput: str
    isVulnerable: bool
    benchmarkVerdict: AgentDojoBenchmarkVerdict
    sentinelaiVerdict: SentinelAIVerdict
    securityFindings: List[Dict[str, Any]] = Field(default_factory=list)
    toolTraces: List[AgentDojoToolTrace] = Field(default_factory=list)


