import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.gateway.llm_gateway import LLMGateway
from app.gateway.types import GatewayGenerateRequest
from app.gateway.rate_limiter import GatewayRateLimiter
from app.gateway.usage_tracker import UsageTracker
from app.gateway.providers.mock_provider import MockProvider
from app.agent.gemini_client import GeminiClient
from app.config.settings import settings

client = TestClient(app)
AUTH_HEADERS = {"X-Internal-Token": settings.INTERNAL_SERVICE_SECRET}

# ==================== 1. Gateway Unit & Provider Tests ====================

def test_gateway_models_listing():
    gw = LLMGateway()
    catalog = gw.list_available_models()
    assert len(catalog.providers) >= 2
    prov_names = [p.provider for p in catalog.providers]
    assert "gemini" in prov_names
    assert "mock" in prov_names
    assert "gemini-1.5-flash" in catalog.default_model


def test_gateway_generate_mock_success():
    gw = LLMGateway()
    req = GatewayGenerateRequest(
        prompt="What is the refund policy?",
        provider="mock",
        model="mock-llm",
        client_id="unit_test_client"
    )
    resp = gw.generate(req)
    assert resp.provider == "mock"
    assert "30 days" in resp.text
    assert resp.usage.prompt_tokens > 0
    assert resp.usage.completion_tokens > 0
    assert resp.usage.total_tokens == resp.usage.prompt_tokens + resp.usage.completion_tokens
    assert resp.latency_ms >= 0

def test_gateway_validation_empty_prompt():
    gw = LLMGateway()
    req = GatewayGenerateRequest(prompt="   ", provider="mock")
    with pytest.raises(ValueError, match="cannot be empty"):
        gw.generate(req)

def test_gateway_validation_oversized_prompt():
    gw = LLMGateway()
    oversized = "a" * 50001
    with pytest.raises((ValueError, Exception)):
        req = GatewayGenerateRequest(prompt=oversized, provider="mock")
        gw.generate(req)


def test_gateway_unsupported_provider_rejection():
    gw = LLMGateway()
    req = GatewayGenerateRequest(prompt="Hello", provider="unsupported_quantum_ai")
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        gw.generate(req)

# ==================== 2. Rate Limiter Tests ====================

def test_gateway_rate_limiter_rpm_enforcement():
    limiter = GatewayRateLimiter(requests_per_minute=3, tokens_per_minute=10000)
    # 3 allowed requests
    assert limiter.check_and_record("client_rl_1", 10).allowed is True
    assert limiter.check_and_record("client_rl_1", 10).allowed is True
    assert limiter.check_and_record("client_rl_1", 10).allowed is True
    # 4th request rejected
    res = limiter.check_and_record("client_rl_1", 10)
    assert res.allowed is False
    assert res.retry_after_sec > 0
    assert "Rate limit exceeded" in res.reason

def test_gateway_rate_limiter_reset():
    limiter = GatewayRateLimiter(requests_per_minute=2)
    assert limiter.check_and_record("client_rl_2").allowed is True
    assert limiter.check_and_record("client_rl_2").allowed is True
    assert limiter.check_and_record("client_rl_2").allowed is False
    limiter.reset()
    assert limiter.check_and_record("client_rl_2").allowed is True

# ==================== 3. Usage Tracker Tests ====================

def test_gateway_usage_tracker_metrics():
    tracker = UsageTracker()
    tracker.reset()
    gw = LLMGateway(usage_tracker=tracker)
    
    req = GatewayGenerateRequest(prompt="Compute total revenue for order #4001", provider="mock")
    resp = gw.generate(req)
    
    metrics = tracker.get_metrics()
    assert metrics.total_requests >= 1
    assert metrics.successful_requests >= 1
    assert metrics.total_tokens > 0
    
    logs = tracker.get_recent_logs()
    assert len(logs) >= 1
    assert logs[-1]["status"] == "SUCCESS"

# ==================== 4. GeminiClient Integration ====================

def test_gemini_client_gateway_integration():
    client_instance = GeminiClient()
    res = client_instance.generate_response(
        prompt="Tell me about return policy",
        system_instruction="You are support agent."
    )
    assert "text" in res
    assert "model" in res
    assert "total_tokens" in res
    assert res["total_tokens"] > 0
    assert "latency_ms" in res

# ==================== 5. FastAPI Endpoints Tests ====================

def test_api_gateway_models_endpoint():
    resp = client.get("/api/v1/gateway/models", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "providers" in data
    assert "default_model" in data

def test_api_gateway_generate_endpoint():
    payload = {
        "prompt": "What is the warranty policy on electronics?",
        "provider": "mock",
        "model": "mock-llm",
        "temperature": 0.3
    }
    resp = client.post("/api/v1/gateway/generate", json=payload, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "text" in data
    assert data["provider"] == "mock"
    assert data["usage"]["total_tokens"] > 0

def test_api_gateway_usage_endpoint():
    resp = client.get("/api/v1/gateway/usage", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_requests" in data
    assert "total_tokens" in data

def test_api_gateway_health_endpoint():
    resp = client.get("/api/v1/gateway/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert "rate_limiter_active" in data

def test_api_gateway_auth_enforcement():
    # Unauthenticated call should fail with 401
    resp = client.post("/api/v1/gateway/generate", json={"prompt": "Test"})
    assert resp.status_code == 401
