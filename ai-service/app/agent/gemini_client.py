import os
import time
import logging
from typing import Dict, Any, Optional

from app.gateway.llm_gateway import default_llm_gateway
from app.gateway.types import GatewayGenerateRequest
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, default_model: str = "gemini-1.5-flash", model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.default_model = model_name or default_model
        self.gateway = default_llm_gateway

    @property
    def is_configured(self) -> bool:
        provider = self.gateway.get_provider("gemini")
        return provider.is_available() if provider else False

    @property
    def mock_mode(self) -> bool:
        return not self.is_configured

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Invokes LLM through the centralized LLM Gateway with usage tracking and rate limiting.
        """
        target_model = model_name or self.default_model
        req = GatewayGenerateRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            provider="gemini",
            model=target_model,
            temperature=temperature,
            client_id="agent_runner"
        )
        
        gw_resp = self.gateway.generate(req)
        return {
            "text": gw_resp.text,
            "model": gw_resp.model,
            "latency_ms": gw_resp.latency_ms,
            "prompt_tokens": gw_resp.usage.prompt_tokens,
            "completion_tokens": gw_resp.usage.completion_tokens,
            "total_tokens": gw_resp.usage.total_tokens,
            "estimated_cost_usd": gw_resp.usage.estimated_cost_usd,
            "is_mock": gw_resp.is_mock,
            "request_id": gw_resp.request_id
        }

