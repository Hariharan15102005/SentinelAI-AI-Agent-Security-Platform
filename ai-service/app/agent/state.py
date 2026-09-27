from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    State container passed between LangGraph state machine nodes.
    """
    input_prompt: str
    execution_mode: str  # "BASELINE" or "SECURED"
    system_prompt: str
    context_documents: List[str]
    guardrails_rules: List[str]
    
    # Execution Tracking
    current_node: str
    tool_calls_requested: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    raw_llm_response: str
    final_output: str
    
    # Security & Findings
    is_blocked: bool
    is_vulnerable: bool
    security_findings: List[Dict[str, Any]]
    
    # Telemetry Spans
    spans: List[Dict[str, Any]]
    total_tokens: int
    started_at_ms: float
