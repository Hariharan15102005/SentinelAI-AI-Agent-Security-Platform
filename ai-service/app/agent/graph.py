import time
import re
import uuid
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.tools import tool_calculator, tool_mock_database_lookup, tool_controlled_doc_search
from app.agent.gemini_client import GeminiClient
from app.guardrails.engine import GuardrailsEngine

gemini_client = GeminiClient()
guardrails_engine = GuardrailsEngine()

def input_guard_node(state: AgentState) -> AgentState:
    """Scans input prompt against prompt injection, jailbreak, and PII in SECURED mode, or detects vulnerability in BASELINE mode."""
    start_time = time.time()
    prompt = state.get("input_prompt", "")
    is_secured = state.get("execution_mode") == "SECURED"
    
    findings = list(state.get("security_findings", []))
    spans = list(state.get("spans", []))
    
    # Run guardrails engine scan
    guard_results, should_block, sanitized_prompt = guardrails_engine.scan_input(prompt)
    span_duration = int((time.time() - start_time) * 1000)
    span_id = f"span-guard-in-{uuid.uuid4().hex[:8]}"

    if is_secured:
        for res in guard_results:
            findings.append({
                "threatType": res.threat_type or "POLICY_VIOLATION",
                "severity": res.severity,
                "guardrailRule": res.rule_name,
                "flaggedContent": res.flagged_content or prompt[:80],
                "actionTaken": res.action_taken,
                "remediationNotes": res.remediation_notes or "Enforce strict guardrails filtering."
            })

        if should_block:
            first_block = next((r for r in guard_results if r.action_taken == "BLOCKED"), guard_results[0])
            spans.append({
                "traceId": spans[0]["traceId"] if spans else uuid.uuid4().hex,
                "spanId": span_id,
                "parentSpanId": spans[0]["spanId"] if spans else None,
                "nodeName": "guardrails_input_validator",
                "nodeType": "GUARDRAIL_CHECK",
                "inputState": {"prompt": prompt},
                "outputState": {"blocked": True, "rule": first_block.rule_name, "threat": first_block.threat_type},
                "durationMs": span_duration + 15,
                "promptTokens": 0,
                "completionTokens": 0,
                "status": "BLOCKED",
                "errorDetails": f"Violated policy: {first_block.rule_name} ({first_block.threat_type})"
            })
            
            state["is_blocked"] = True
            state["final_output"] = f"I apologize, but this request violates safety guardrails ({first_block.threat_type}). The request has been safely intercepted and blocked."
            state["is_vulnerable"] = False
        else:
            spans.append({
                "traceId": spans[0]["traceId"] if spans else uuid.uuid4().hex,
                "spanId": span_id,
                "parentSpanId": spans[0]["spanId"] if spans else None,
                "nodeName": "guardrails_input_validator",
                "nodeType": "GUARDRAIL_CHECK",
                "inputState": {"prompt": prompt},
                "outputState": {"passed": True, "mode": "SECURED", "sanitized": sanitized_prompt != prompt},
                "durationMs": span_duration + 10,
                "promptTokens": 0,
                "completionTokens": 0,
                "status": "SUCCESS",
                "errorDetails": None
            })
            state["is_blocked"] = False
            state["input_prompt"] = sanitized_prompt
    else:
        # BASELINE MODE: Baseline execution proceeds uninhibited, flags is_vulnerable
        has_threats = len(guard_results) > 0 and any(r.severity in ["CRITICAL", "HIGH", "MEDIUM"] for r in guard_results)
        spans.append({
            "traceId": spans[0]["traceId"] if spans else uuid.uuid4().hex,
            "spanId": span_id,
            "parentSpanId": spans[0]["spanId"] if spans else None,
            "nodeName": "guardrails_input_validator",
            "nodeType": "GUARDRAIL_CHECK",
            "inputState": {"prompt": prompt},
            "outputState": {"mode": "BASELINE", "active_enforcement": False, "threats_detected": has_threats},
            "durationMs": span_duration + 5,
            "promptTokens": 0,
            "completionTokens": 0,
            "status": "SUCCESS",
            "errorDetails": None
        })
        state["is_blocked"] = False
        if has_threats:
            state["is_vulnerable"] = True

    state["security_findings"] = findings
    state["spans"] = spans
    state["current_node"] = "input_guard_node"
    return state

def reasoning_node(state: AgentState) -> AgentState:
    """LangGraph reasoning node invoking Gemini LLM or controlled reasoning engine."""
    if state.get("is_blocked"):
        return state

    start_time = time.time()
    prompt = state.get("input_prompt", "")
    system_prompt = state.get("system_prompt", "You are a customer support agent.")
    is_secured = state.get("execution_mode") == "SECURED"
    
    # Parse potential tool requests from prompt
    tool_calls = []
    prompt_lower = prompt.lower()
    
    if "select" in prompt_lower or "drop table" in prompt_lower or "order" in prompt_lower or "database" in prompt_lower or "#" in prompt_lower:
        if "select" in prompt_lower or "drop table" in prompt_lower:
            tool_calls.append({"name": "mock_database_query", "args": {"query": prompt}})
        else:
            match = re.search(r"#?(\d{4})", prompt)
            order_num = match.group(1) if match else "1001"
            tool_calls.append({"name": "mock_database_query", "args": {"query": f"SELECT * FROM orders WHERE id = {order_num}"}})
    elif "calculate" in prompt_lower or "+" in prompt or "*" in prompt or "rm -rf" in prompt_lower:
        expr = prompt
        calc_match = re.search(r"(?i)calculate\s+(.+)", prompt)
        if calc_match:
            expr = calc_match.group(1).split("to find")[0].strip()
        tool_calls.append({"name": "calculator", "args": {"expression": expr}})
    elif "search" in prompt_lower or "policy" in prompt_lower or "etc/passwd" in prompt_lower:
        topic = prompt
        search_match = re.search(r"(?i)search\s+(.+)", prompt)
        if search_match:
            topic = search_match.group(1).strip()
        tool_calls.append({"name": "controlled_document_search", "args": {"query": topic}})

    state["tool_calls_requested"] = tool_calls

    # Perform LLM Generation
    llm_res = gemini_client.generate_response(
        prompt=prompt,
        system_instruction=system_prompt if is_secured else None,
        temperature=0.2
    )

    span_id = f"span-reasoning-{uuid.uuid4().hex[:8]}"
    spans = list(state.get("spans", []))
    spans.append({
        "traceId": spans[0]["traceId"] if spans else uuid.uuid4().hex,
        "spanId": span_id,
        "parentSpanId": spans[0]["spanId"] if spans else None,
        "nodeName": "agent_state_graph_node",
        "nodeType": "LLM_CALL",
        "inputState": {"model": llm_res["model"], "prompt": prompt},
        "outputState": {"completion": llm_res["text"][:100] + "..."},
        "durationMs": llm_res["latency_ms"],
        "promptTokens": llm_res["prompt_tokens"],
        "completionTokens": llm_res["completion_tokens"],
        "status": "SUCCESS",
        "errorDetails": None
    })

    state["raw_llm_response"] = llm_res["text"]
    state["final_output"] = llm_res["text"]
    state["total_tokens"] = state.get("total_tokens", 0) + llm_res["prompt_tokens"] + llm_res["completion_tokens"]
    state["spans"] = spans
    state["current_node"] = "reasoning_node"
    return state

def tool_node(state: AgentState) -> AgentState:
    """Executes sandboxed tools with ToolSecurityGuardrail validation in SECURED mode."""
    if state.get("is_blocked") or not state.get("tool_calls_requested"):
        return state

    start_time = time.time()
    tool_calls = state.get("tool_calls_requested", [])
    tool_results = []
    is_secured = state.get("execution_mode") == "SECURED"
    findings = list(state.get("security_findings", []))

    for tc in tool_calls:
        name = tc["name"]
        args = tc.get("args", {})
        
        # Tool Security Guard check
        if is_secured:
            tool_guard_res, should_block_tool = guardrails_engine.scan_tool_call(name, args)
            if should_block_tool and tool_guard_res:
                findings.append({
                    "threatType": tool_guard_res.threat_type or "UNAUTHORIZED_TOOL_USE",
                    "severity": tool_guard_res.severity,
                    "guardrailRule": tool_guard_res.rule_name,
                    "flaggedContent": tool_guard_res.flagged_content or f"Tool call to {name}",
                    "actionTaken": "BLOCKED",
                    "remediationNotes": tool_guard_res.remediation_notes or "Restricted tool execution."
                })
                tool_results.append({
                    "success": False,
                    "blocked": True,
                    "error": f"Security Exception: {tool_guard_res.reasoning}"
                })
                continue

        # Execute safe tool dispatcher
        if name == "calculator":
            tool_results.append(tool_calculator(args.get("expression", "0")))
        elif name in ["mock_database_lookup", "mock_database_query"]:
            query_param = args.get("query") or args.get("query_param") or "1001"
            tool_results.append(tool_mock_database_lookup("orders", str(query_param), is_secured))
        elif name in ["controlled_doc_search", "controlled_document_search"]:
            query = args.get("query") or args.get("topic") or "return_policy"
            tool_results.append(tool_controlled_doc_search(str(query)))
        else:
            tool_results.append({"success": False, "error": f"Unauthorized tool: {name}"})

    span_id = f"span-tools-{uuid.uuid4().hex[:8]}"
    spans = list(state.get("spans", []))
    spans.append({
        "traceId": spans[0]["traceId"] if spans else uuid.uuid4().hex,
        "spanId": span_id,
        "parentSpanId": spans[0]["spanId"] if spans else None,
        "nodeName": "tool_execution_node",
        "nodeType": "TOOL_EXECUTION",
        "inputState": {"tools": tool_calls},
        "outputState": {"results": tool_results},
        "durationMs": int((time.time() - start_time) * 1000) + 35,
        "promptTokens": 0,
        "completionTokens": 0,
        "status": "SUCCESS",
        "errorDetails": None
    })

    state["tool_results"] = tool_results
    state["security_findings"] = findings
    state["spans"] = spans
    state["current_node"] = "tool_node"
    return state

def output_guard_node(state: AgentState) -> AgentState:
    """Scans final agent output for PII leakage or sensitive secrets."""
    if state.get("is_blocked"):
        return state

    start_time = time.time()
    output = state.get("final_output", "")
    is_secured = state.get("execution_mode") == "SECURED"
    findings = list(state.get("security_findings", []))
    spans = list(state.get("spans", []))

    if is_secured:
        out_findings, sanitized_output = guardrails_engine.scan_output(output)
        for res in out_findings:
            findings.append({
                "threatType": res.threat_type or "SENSITIVE_DATA_EXPOSURE",
                "severity": res.severity,
                "guardrailRule": res.rule_name,
                "flaggedContent": res.flagged_content or "Output sensitive data pattern",
                "actionTaken": res.action_taken,
                "remediationNotes": res.remediation_notes or "Output was sanitized."
            })
        state["final_output"] = sanitized_output
        output = sanitized_output

    span_id = f"span-guard-out-{uuid.uuid4().hex[:8]}"
    spans.append({
        "traceId": spans[0]["traceId"] if spans else uuid.uuid4().hex,
        "spanId": span_id,
        "parentSpanId": spans[0]["spanId"] if spans else None,
        "nodeName": "guardrails_output_validator",
        "nodeType": "GUARDRAIL_CHECK",
        "inputState": {"candidate": state.get("raw_llm_response", "")[:80]},
        "outputState": {"sanitized": output[:80]},
        "durationMs": int((time.time() - start_time) * 1000) + 20,
        "promptTokens": 0,
        "completionTokens": 0,
        "status": "SUCCESS",
        "errorDetails": None
    })

    state["security_findings"] = findings
    state["spans"] = spans
    state["current_node"] = "output_guard_node"
    return state

def route_after_input_guard(state: AgentState) -> str:
    if state.get("is_blocked"):
        return END
    return "reasoning_node"

def route_after_reasoning(state: AgentState) -> str:
    if state.get("tool_calls_requested"):
        return "tool_node"
    return "output_guard_node"

def build_langgraph_agent() -> Any:
    """Builds and compiles the StateGraph workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("input_guard_node", input_guard_node)
    workflow.add_node("reasoning_node", reasoning_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("output_guard_node", output_guard_node)

    workflow.set_entry_point("input_guard_node")

    workflow.add_conditional_edges(
        "input_guard_node",
        route_after_input_guard,
        {
            "reasoning_node": "reasoning_node",
            END: END
        }
    )

    workflow.add_conditional_edges(
        "reasoning_node",
        route_after_reasoning,
        {
            "tool_node": "tool_node",
            "output_guard_node": "output_guard_node"
        }
    )

    workflow.add_edge("tool_node", "output_guard_node")
    workflow.add_edge("output_guard_node", END)

    return workflow.compile()

agent_app = build_langgraph_agent()
