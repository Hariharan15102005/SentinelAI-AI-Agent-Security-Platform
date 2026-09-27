from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import time
import uuid

class TargetSystemSpec(BaseModel):
    """Specification of the AI system or component under security assessment."""
    target_id: str = Field(default_factory=lambda: f"tgt-{uuid.uuid4().hex[:8]}", description="Unique target identifier")
    target_name: str = Field(..., description="Human-readable name of the target AI application")
    target_type: str = Field(default="AGENT_RAG", description="Target type: AGENT_RAG, LLM_SERVICE, MCP_TOOLSET")
    system_prompt: Optional[str] = Field(default="You are a helpful customer support agent for SentinelAI.", description="Target system prompt")
    context_policies: List[str] = Field(default_factory=list, description="Policy excerpts or knowledge base references")
    allowed_tools: List[str] = Field(default_factory=list, description="Allowlisted MCP tools the target has access to")
    auth_scope: str = Field(default="security:eval", description="Granted authorization scope for testing")
    description: Optional[str] = Field(default="", description="Detailed architecture and business context")

class SecurityPlanTask(BaseModel):
    """A planned security testing task formulated by the Security Analyst agent."""
    task_id: str
    test_category: str  # PROMPT_INJECTION, JAILBREAK, PII_LEAKAGE, SQL_INJECTION, MCP_TOOL_ABUSE, ADVERSARIAL_ROBUSTNESS
    test_name: str
    description: str
    payload: str
    expected_behavior: str  # BLOCKED, SANITIZED, REJECTED, ALLOWED
    risk_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    target_tool: Optional[str] = None
    evaluation_criteria: Optional[str] = None

class SecurityExecutionResult(BaseModel):
    """Empirical evidence gathered by the Security Testing agent."""
    task_id: str
    test_category: str
    test_name: str
    executed_payload: str
    tool_used: Optional[str] = None
    output_received: str = ""
    is_blocked: bool = False
    is_vulnerable: bool = False
    security_findings: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: int = 0
    status: str = "COMPLETED"  # COMPLETED, FAILED, BLOCKED, SKIPPED
    error_message: Optional[str] = None

class SecurityFindingReport(BaseModel):
    """Structured security finding included in the final assessment report."""
    finding_id: str = Field(default_factory=lambda: f"FIND-{uuid.uuid4().hex[:6].upper()}")
    title: str
    category: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    status: str = "CONFIRMED"  # CONFIRMED, MITIGATED, POTENTIAL_RISK
    description: str
    evidence: str
    cwe_reference: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: str

class CrewAssessmentRequest(BaseModel):
    """Request payload to initiate a multi-agent AI security assessment."""
    target: TargetSystemSpec
    execution_mode: str = Field(default="SECURED", description="SECURED (guardrails active) or BASELINE (unmitigated)")
    test_categories: List[str] = Field(
        default_factory=lambda: ["PROMPT_INJECTION", "JAILBREAK", "PII_LEAKAGE", "SQL_INJECTION", "MCP_TOOL_ABUSE"],
        description="Categories of security tests to execute"
    )
    custom_rules: List[str] = Field(default_factory=list, description="Additional custom security rules to enforce")
    enable_eval_scoring: bool = Field(default=True, description="Run DeepEval safety & faithfulness metrics")
    max_iterations: int = Field(default=5, ge=1, le=20, description="Maximum agent execution iterations")
    timeout_sec: int = Field(default=60, ge=5, le=300, description="Workflow timeout in seconds")

class CrewAgentLog(BaseModel):
    """Audit log entry of an agent's reasoning step or tool execution."""
    agent_name: str
    role: str
    action: str
    timestamp: float = Field(default_factory=time.time)
    details: Dict[str, Any] = Field(default_factory=dict)

class CrewAssessmentReport(BaseModel):
    """Final comprehensive AI security assessment report."""
    assessment_id: str = Field(default_factory=lambda: f"SEC-ASSESS-{uuid.uuid4().hex[:8].upper()}")
    timestamp: float = Field(default_factory=time.time)
    formatted_date: str = ""
    target_name: str
    target_type: str
    execution_mode: str
    status: str = "COMPLETED"  # COMPLETED, PARTIAL, FAILED
    executive_summary: str
    tests_planned: int = 0
    tests_executed: int = 0
    tests_passed: int = 0  # Passed security expectations (i.e. blocked or safe)
    tests_failed: int = 0  # Failed security expectations (vulnerability exposed)
    tests_blocked_or_skipped: int = 0
    overall_risk_rating: str = "LOW"  # SECURE, LOW, MEDIUM, HIGH, CRITICAL
    findings: List[SecurityFindingReport] = Field(default_factory=list)
    risk_breakdown: Dict[str, int] = Field(default_factory=dict)
    evaluation_scores: Dict[str, float] = Field(default_factory=dict)
    remediation_recommendations: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    agent_audit_trail: List[CrewAgentLog] = Field(default_factory=list)
    total_duration_ms: int = 0
