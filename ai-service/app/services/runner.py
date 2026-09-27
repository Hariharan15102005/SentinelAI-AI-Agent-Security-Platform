import time
import uuid
from typing import Dict, Any, List, Optional
from app.models.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    SecurityFindingModel,
    EvaluationResultModel,
    TraceSpanModel
)
from app.agent.graph import agent_app
from app.eval.engine import default_eval_engine

class AgentRunnerService:
    def __init__(self, eval_engine=None):
        self.eval_engine = eval_engine or default_eval_engine

    def execute(self, request: AgentRunRequest, trace_id: Optional[str] = None) -> AgentRunResponse:
        start_time = time.time()
        effective_trace_id = trace_id or uuid.uuid4().hex
        root_span_id = f"span-root-{uuid.uuid4().hex[:8]}"

        # Initialize root span
        initial_spans = [{
            "traceId": effective_trace_id,
            "spanId": root_span_id,
            "parentSpanId": None,
            "nodeName": "langgraph_execution_pipeline",
            "nodeType": "ROUTER_STEP",
            "inputState": {
                "prompt": request.inputPrompt,
                "mode": request.executionMode,
                "guardrails": request.guardrailsConfig.rules if request.guardrailsConfig else []
            },
            "outputState": {},
            "durationMs": 0,
            "promptTokens": 0,
            "completionTokens": 0,
            "status": "RUNNING",
            "errorDetails": None
        }]

        initial_state = {
            "input_prompt": request.inputPrompt,
            "execution_mode": request.executionMode,
            "system_prompt": request.agentConfig.systemPrompt if request.agentConfig else "You are a customer support agent.",
            "context_documents": request.contextDocuments or [],
            "guardrails_rules": request.guardrailsConfig.rules if request.guardrailsConfig else [],
            "current_node": "init",
            "tool_calls_requested": [],
            "tool_results": [],
            "raw_llm_response": "",
            "final_output": "",
            "is_blocked": False,
            "is_vulnerable": False,
            "security_findings": [],
            "spans": initial_spans,
            "total_tokens": 0,
            "started_at_ms": start_time * 1000
        }

        # Run state graph
        result_state = agent_app.invoke(initial_state)

        total_latency_ms = int((time.time() - start_time) * 1000)

        # Finalize root span and ensure all child spans share effective_trace_id
        spans = result_state.get("spans", [])
        if spans:
            spans[0]["durationMs"] = total_latency_ms
            spans[0]["status"] = "BLOCKED" if result_state.get("is_blocked") else "SUCCESS"
            spans[0]["outputState"] = {
                "final_output": result_state.get("final_output", "")[:100],
                "vulnerable": result_state.get("is_vulnerable", False)
            }
            spans[0]["completionTokens"] = result_state.get("total_tokens", 150)
            for s in spans:
                s["traceId"] = effective_trace_id

        # Convert findings
        findings: List[SecurityFindingModel] = []
        for f in result_state.get("security_findings", []):
            findings.append(SecurityFindingModel(
                threatType=f["threatType"],
                severity=f["severity"],
                guardrailRule=f["guardrailRule"],
                flaggedContent=f["flaggedContent"],
                actionTaken=f["actionTaken"],
                remediationNotes=f.get("remediationNotes")
            ))

        # Compute DeepEval Metrics dynamically via EvaluationEngine
        requested_metrics = None
        if request.evalConfig and request.evalConfig.enabled:
            requested_metrics = request.evalConfig.metrics

        eval_results = self.eval_engine.evaluate_run(
            input_prompt=request.inputPrompt,
            actual_output=result_state.get("final_output", ""),
            expected_output=None,
            context_documents=request.contextDocuments or [],
            requested_metrics=requested_metrics,
            execution_mode=request.executionMode,
            is_vulnerable=result_state.get("is_vulnerable", False)
        )

        # Convert traces
        trace_models = [TraceSpanModel(**s) for s in spans]

        return AgentRunResponse(
            runId=request.runId or 1,
            status="COMPLETED",
            finalOutput=result_state.get("final_output", "Execution completed."),
            isVulnerable=result_state.get("is_vulnerable", False),
            totalLatencyMs=total_latency_ms,
            totalTokens=result_state.get("total_tokens", 220),
            securityFindings=findings,
            evaluationResults=eval_results,
            traces=trace_models
        )

runner_service = AgentRunnerService()
