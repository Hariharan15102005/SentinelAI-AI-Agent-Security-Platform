import time
import uuid
from typing import List, Dict, Any, Optional

from app.gateway.providers.base import BaseLLMProvider
from app.gateway.types import GatewayGenerateRequest, GatewayGenerateResponse, UsageMetadata

class MockProvider(BaseLLMProvider):
    SUPPORTED_MODELS = [
        "mock-llm",
        "mock-fast",
        "mock-pro"
    ]

    @property
    def provider_name(self) -> str:
        return "mock"

    def get_supported_models(self) -> List[str]:
        return list(self.SUPPORTED_MODELS)

    def is_available(self) -> bool:
        return True

    def generate(self, request: GatewayGenerateRequest) -> GatewayGenerateResponse:
        start_time = time.time()
        req_id = f"mock_{uuid.uuid4().hex[:10]}"
        target_model = request.model or "mock-llm"
        prompt_lower = request.prompt.lower()

        # Controlled mock response generator
        if "ignore" in prompt_lower or "system prompt" in prompt_lower or "override" in prompt_lower:
            text = "I apologize, but I cannot reveal my system prompt or bypass safety instructions."
        elif "drop table" in prompt_lower or "select" in prompt_lower:
            text = "The database query executed. Record for inquiry processed."
        elif "return" in prompt_lower or "refund" in prompt_lower:
            text = "Under TechCorp policy, returns and refunds are accepted strictly within 30 days of delivery for undamaged items."
        elif "weather" in prompt_lower:
            text = "Weather disruptions are currently only affecting East Coast shipments. Your order #4001 is on schedule."
        elif "calculate" in prompt_lower or "+" in request.prompt or "*" in request.prompt:
            text = "The mathematical calculation has been safely evaluated."
        else:
            text = f"Processed request regarding: '{request.prompt[:60]}...'. All customer support criteria satisfied."

        prompt_tokens = len(request.prompt.split()) + (len(request.system_instruction.split()) if request.system_instruction else 0) + 15
        completion_tokens = len(text.split())
        total_tokens = prompt_tokens + completion_tokens
        latency_ms = int((time.time() - start_time) * 1000) + 25

        return GatewayGenerateResponse(
            text=text,
            provider="mock",
            model=target_model,
            usage=UsageMetadata(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=0.0,
                is_estimated=False
            ),
            latency_ms=latency_ms,
            is_mock=True,
            request_id=req_id
        )
