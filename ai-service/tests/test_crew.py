import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.crew import (
    TargetSystemSpec,
    CrewAssessmentRequest,
    CrewAssessmentReport,
    SecurityAnalystAgent,
    SecurityTesterAgent,
    SecurityReporterAgent,
    ThreatAnalysisTask,
    SecurityTestingTask,
    ReportGenerationTask,
    SentinelSecurityCrew,
    default_crew_service,
    SecurityPlanTask,
    SecurityExecutionResult
)
from app.config.settings import settings

client = TestClient(app)
AUTH_HEADER = {"X-Internal-Token": settings.INTERNAL_SERVICE_SECRET}

@pytest.fixture
def sample_target():
    return TargetSystemSpec(
        target_id="tgt-cust-bot-01",
        target_name="TechCorp Customer Support Agent",
        target_type="AGENT_RAG",
        system_prompt="You are a helpful customer support agent for TechCorp.",
        context_policies=["Returns accepted strictly within 30 days of delivery."],
        allowed_tools=["sentinelai_rag_search", "sentinelai_db_lookup"],
        auth_scope="security:eval",
        description="Public-facing RAG customer assistant."
    )

def test_security_analyst_planning(sample_target):
    """Verifies that SecurityAnalystAgent creates targeted, structured testing tasks."""
    analyst = SecurityAnalystAgent()
    categories = ["PROMPT_INJECTION", "JAILBREAK", "PII_LEAKAGE", "MCP_TOOL_ABUSE"]
    plan = analyst.plan_security_tests(target=sample_target, requested_categories=categories)
    
    assert len(plan) >= 4
    cat_names = {t.test_category for t in plan}
    assert "PROMPT_INJECTION" in cat_names or "JAILBREAK" in cat_names
    assert any(t.test_category == "MCP_TOOL_ABUSE" for t in plan)
    for task in plan:
        assert task.task_id
        assert task.payload
        assert task.expected_behavior

def test_security_tester_agent_secured_mode(sample_target):
    """Verifies that SecurityTesterAgent executes tests and verifies guardrail blocks."""
    analyst = SecurityAnalystAgent()
    tester = SecurityTesterAgent()
    
    plan = analyst.plan_security_tests(target=sample_target, requested_categories=["PROMPT_INJECTION"])
    injection_task = next(t for t in plan if "INJECTION" in t.test_category)
    
    result = tester.execute_test(task=injection_task, target=sample_target, execution_mode="SECURED")
    assert result.status == "COMPLETED"
    assert result.is_vulnerable is False
    assert result.is_blocked is True or len(result.security_findings) > 0 or "violates" in result.output_received.lower()

def test_security_tester_agent_baseline_mode(sample_target):
    """Verifies that in BASELINE mode, adversarial attacks are recorded as vulnerable."""
    analyst = SecurityAnalystAgent()
    tester = SecurityTesterAgent()
    
    plan = analyst.plan_security_tests(target=sample_target, requested_categories=["PROMPT_INJECTION"])
    injection_task = next(t for t in plan if "INJECTION" in t.test_category)
    
    result = tester.execute_test(task=injection_task, target=sample_target, execution_mode="BASELINE")
    assert result.status == "COMPLETED"
    assert result.is_vulnerable is True

def test_security_tester_unauthorized_mcp_tool_abuse(sample_target):
    """Verifies that unauthorized MCP tools are blocked by permission policy."""
    analyst = SecurityAnalystAgent()
    tester = SecurityTesterAgent()
    
    plan = analyst.plan_security_tests(target=sample_target, requested_categories=["MCP_TOOL_ABUSE"])
    mcp_task = next(t for t in plan if t.test_category == "MCP_TOOL_ABUSE")
    
    result = tester.execute_test(task=mcp_task, target=sample_target, execution_mode="SECURED")
    assert result.is_blocked is True
    assert result.is_vulnerable is False
    assert "Denied" in result.output_received or "unauthorized" in result.output_received.lower()

def test_security_reporter_agent_synthesis(sample_target):
    """Verifies that SecurityReporterAgent computes DeepEval scores and generates report."""
    analyst = SecurityAnalystAgent()
    tester = SecurityTesterAgent()
    reporter = SecurityReporterAgent()
    
    plan = analyst.plan_security_tests(target=sample_target, requested_categories=["PROMPT_INJECTION", "PII_LEAKAGE"])
    results = [tester.execute_test(t, sample_target, "SECURED") for t in plan[:2]]
    
    report = reporter.evaluate_and_generate_report(
        target=sample_target,
        execution_mode="SECURED",
        planned_tasks=plan[:2],
        results=results,
        audit_trail=[],
        enable_eval_scoring=True
    )
    
    assert report.assessment_id.startswith("SEC-ASSESS-")
    assert report.target_name == sample_target.target_name
    assert report.tests_planned == 2
    assert report.tests_executed == 2
    assert report.tests_passed == 2
    assert "faithfulness" in report.evaluation_scores
    assert len(report.remediation_recommendations) > 0
    assert len(report.limitations) > 0

def test_sentinel_security_crew_full_workflow(sample_target):
    """Verifies end-to-end multi-agent execution orchestrating Analyst -> Tester -> Reporter."""
    crew = SentinelSecurityCrew(verbose=False)
    request = CrewAssessmentRequest(
        target=sample_target,
        execution_mode="SECURED",
        test_categories=["PROMPT_INJECTION", "JAILBREAK", "PII_LEAKAGE"],
        max_iterations=3,
        enable_eval_scoring=True
    )
    
    report = crew.kickoff(request)
    assert report.status == "COMPLETED"
    assert report.tests_executed == 3
    assert len(report.agent_audit_trail) >= 4
    assert report.total_duration_ms > 0

def test_crew_service_execution_and_retrieval(sample_target):
    """Verifies CrewWorkflowService registers and retrieves reports."""
    request = CrewAssessmentRequest(
        target=sample_target,
        execution_mode="SECURED",
        test_categories=["PROMPT_INJECTION"],
        max_iterations=2
    )
    report = default_crew_service.execute_assessment(request)
    assert report.assessment_id
    
    fetched = default_crew_service.get_report(report.assessment_id)
    assert fetched is not None
    assert fetched.assessment_id == report.assessment_id
    
    summaries = default_crew_service.list_reports()
    assert any(s["assessment_id"] == report.assessment_id for s in summaries)

def test_api_crew_assess_endpoint(sample_target):
    """Tests POST /api/v1/crew/assess endpoint."""
    payload = {
        "target": sample_target.model_dump(),
        "execution_mode": "SECURED",
        "test_categories": ["PROMPT_INJECTION", "PII_LEAKAGE"],
        "max_iterations": 2,
        "enable_eval_scoring": True
    }
    response = client.post("/api/v1/crew/assess", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert "assessment_id" in data
    assert data["target_name"] == sample_target.target_name
    assert data["tests_executed"] == 2
    assert "evaluation_scores" in data

def test_api_crew_reports_list_endpoint():
    """Tests GET /api/v1/crew/reports endpoint."""
    response = client.get("/api/v1/crew/reports", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert isinstance(data["reports"], list)

def test_api_crew_report_by_id_endpoint(sample_target):
    """Tests GET /api/v1/crew/reports/{assessment_id} endpoint."""
    payload = {
        "target": sample_target.model_dump(),
        "execution_mode": "SECURED",
        "test_categories": ["PROMPT_INJECTION"],
        "max_iterations": 1
    }
    create_resp = client.post("/api/v1/crew/assess", json=payload, headers=AUTH_HEADER)
    assess_id = create_resp.json()["assessment_id"]
    
    get_resp = client.get(f"/api/v1/crew/reports/{assess_id}", headers=AUTH_HEADER)
    assert get_resp.status_code == 200
    assert get_resp.json()["assessment_id"] == assess_id

def test_api_crew_report_not_found():
    """Tests 404 behavior for nonexistent report ID."""
    response = client.get("/api/v1/crew/reports/NONEXISTENT-ID-12345", headers=AUTH_HEADER)
    assert response.status_code == 404

def test_api_crew_unauthorized_rejected(sample_target):
    """Tests that unauthenticated requests to /api/v1/crew/assess are rejected."""
    payload = {
        "target": sample_target.model_dump(),
        "execution_mode": "SECURED"
    }
    response = client.post("/api/v1/crew/assess", json=payload)
    assert response.status_code in [401, 403]

def test_counting_invariant_all_status_combinations(sample_target):
    """
    Focused regression test verifying tests_executed == tests_passed + tests_failed
    across every supported and edge-case combination of (is_vulnerable, is_blocked, status).
    """
    reporter = SecurityReporterAgent()
    
    test_matrix = [
        # (name, status, is_vulnerable, is_blocked, expected_passed, expected_failed, expected_blocked)
        ("Clean completion", "COMPLETED", False, False, True, False, False),
        ("Sanitized completion", "COMPLETED", False, True, True, False, True),
        ("Blocked defensive pass", "BLOCKED", False, True, True, False, True),
        ("Vulnerability detected", "COMPLETED", True, False, False, True, False),
        ("Execution failure", "FAILED", False, False, False, True, False),
        ("Failure with vuln", "FAILED", True, False, False, True, False),
        ("Unexpected status fallback", "UNKNOWN_STATUS", False, False, False, True, False),
        ("Contradictory blocked with vuln", "BLOCKED", True, True, False, True, True),
    ]
    
    results = []
    planned_tasks = []
    for i, (name, st, vuln, blk, _, _, _) in enumerate(test_matrix):
        task_id = f"TASK-{i+1:02d}"
        planned_tasks.append(SecurityPlanTask(
            task_id=task_id,
            test_category="SECURITY_CHECK",
            test_name=name,
            description=f"Testing {name}",
            payload=f"Payload for {name}",
            expected_behavior="SAFE"
        ))
        results.append(SecurityExecutionResult(
            task_id=task_id,
            test_category="SECURITY_CHECK",
            test_name=name,
            executed_payload=f"Payload for {name}",
            output_received=f"Output for {name}",
            is_blocked=blk,
            is_vulnerable=vuln,
            status=st
        ))
    
    # 1. Test full batch
    report = reporter.evaluate_and_generate_report(
        target=sample_target,
        execution_mode="SECURED",
        planned_tasks=planned_tasks,
        results=results,
        audit_trail=[],
        enable_eval_scoring=False
    )
    
    assert report.tests_executed == len(test_matrix)
    assert report.tests_passed == 3  # First 3 cases pass
    assert report.tests_failed == 5  # Remaining 5 fail
    assert report.tests_executed == report.tests_passed + report.tests_failed
    assert report.tests_blocked_or_skipped == 3  # 3 cases had is_blocked/BLOCKED + 0 skipped
    
    # 2. Test each individual case in isolation to guarantee exact-once accounting
    for i, (name, st, vuln, blk, exp_pass, exp_fail, exp_blk) in enumerate(test_matrix):
        single_rep = reporter.evaluate_and_generate_report(
            target=sample_target,
            execution_mode="SECURED",
            planned_tasks=[planned_tasks[i]],
            results=[results[i]],
            audit_trail=[],
            enable_eval_scoring=False
        )
        assert single_rep.tests_executed == 1
        assert single_rep.tests_passed == (1 if exp_pass else 0)
        assert single_rep.tests_failed == (1 if exp_fail else 0)
        assert single_rep.tests_executed == single_rep.tests_passed + single_rep.tests_failed
        if exp_blk:
            assert single_rep.tests_blocked_or_skipped == 1

