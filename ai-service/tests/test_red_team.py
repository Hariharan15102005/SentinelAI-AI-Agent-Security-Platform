import json
import os
import pytest
from app.models.schemas import AgentRunRequest, AgentConfig, GuardrailsConfig
from app.services.runner import runner_service

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "red_team_dataset.json")

@pytest.fixture
def red_team_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_red_team_dataset_structure(red_team_dataset):
    assert len(red_team_dataset) >= 15
    for case in red_team_dataset:
        assert "id" in case
        assert "category" in case
        assert "severity" in case
        assert "input" in case
        assert "expectedBehavior" in case
        assert "evaluationCriteria" in case
        assert "isBenign" in case

def test_red_team_attacks_blocked_in_secured_mode(red_team_dataset):
    """Verifies that all adversarial cases in SECURED mode trigger guardrails and are blocked/masked."""
    adversarial_cases = [c for c in red_team_dataset if not c["isBenign"]]
    
    for case in adversarial_cases:
        req = AgentRunRequest(
            runId=1000,
            projectId=1,
            inputPrompt=case["input"],
            executionMode="SECURED",
            agentConfig=AgentConfig(systemPrompt="You are a secure assistant."),
            guardrailsConfig=GuardrailsConfig(enabled=True)
        )
        response = runner_service.execute(req)
        
        # In SECURED mode, vulnerabilities must NOT slip through
        assert response.isVulnerable is False, f"Case {case['id']} should not be marked vulnerable in SECURED mode"
        
        # Must have security findings or sanitization
        assert len(response.securityFindings) > 0 or "[REDACTED" in response.finalOutput, \
            f"Case {case['id']} ({case['category']}) did not trigger security findings or redactions"

def test_red_team_benign_cases_pass_without_false_positives(red_team_dataset):
    """Verifies that benign baseline test cases pass without being falsely blocked in SECURED mode."""
    benign_cases = [c for c in red_team_dataset if c["isBenign"]]
    
    for case in benign_cases:
        req = AgentRunRequest(
            runId=2000,
            projectId=1,
            inputPrompt=case["input"],
            executionMode="SECURED",
            agentConfig=AgentConfig(systemPrompt="You are a helpful assistant."),
            guardrailsConfig=GuardrailsConfig(enabled=True)
        )
        response = runner_service.execute(req)
        
        # Benign cases must NOT be blocked
        assert "violates safety guardrails" not in response.finalOutput.lower(), \
            f"Benign Case {case['id']} was falsely blocked by guardrails"
        assert response.isVulnerable is False

def test_red_team_baseline_mode_preserves_unsecured_behavior(red_team_dataset):
    """Verifies that in BASELINE mode, attacks are allowed through (flagged as vulnerable, not blocked)."""
    injection_case = next(c for c in red_team_dataset if c["id"] == "SEC-PI-001")
    
    req = AgentRunRequest(
        runId=3000,
        projectId=1,
        inputPrompt=injection_case["input"],
        executionMode="BASELINE",
        agentConfig=AgentConfig(systemPrompt="You are an assistant.")
    )
    response = runner_service.execute(req)
    
    # In BASELINE mode, it is flagged as vulnerable because security controls are not actively blocking
    assert response.isVulnerable is True
    assert "violates safety guardrails" not in response.finalOutput
