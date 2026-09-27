import os
import time
import uuid
import logging
from typing import List, Dict, Any, Optional

from app.gateway.providers.base import BaseLLMProvider
from app.gateway.types import GatewayGenerateRequest, GatewayGenerateResponse, UsageMetadata
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    # Standard pricing per 1M tokens (USD)
    PRICING = {
        "gemini-1.5-flash": {"prompt": 0.075 / 1_000_000, "completion": 0.30 / 1_000_000},
        "gemini-1.5-pro": {"prompt": 1.25 / 1_000_000, "completion": 5.00 / 1_000_000},
        "default": {"prompt": 0.075 / 1_000_000, "completion": 0.30 / 1_000_000}
    }

    SUPPORTED_MODELS = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._is_configured = False

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._is_configured = True
                logger.info("GeminiProvider: Google Gemini API successfully configured.")
            except Exception as e:
                logger.warning(f"GeminiProvider configuration failed: {e}")
                self._is_configured = False
        else:
            logger.info("GeminiProvider: No live API key present; ready for mock/fallback mode.")

    @property
    def provider_name(self) -> str:
        return "gemini"

    def get_supported_models(self) -> List[str]:
        return list(self.SUPPORTED_MODELS)

    def is_available(self) -> bool:
        return self._is_configured and not settings.MOCK_LLM_MODE

    def generate(self, request: GatewayGenerateRequest) -> GatewayGenerateResponse:
        start_time = time.time()
        req_id = f"req_{uuid.uuid4().hex[:10]}"
        target_model = request.model or settings.DEFAULT_LLM_MODEL
        if target_model not in self.SUPPORTED_MODELS:
            target_model = "gemini-1.5-flash"

        if not self.is_available():
            raise RuntimeError("GeminiProvider is not configured with a valid live API key.")

        import google.generativeai as genai
        generation_config = genai.types.GenerationConfig(
            temperature=request.temperature if request.temperature is not None else 0.2,
            max_output_tokens=request.max_output_tokens or 1000
        )
        gen_model = genai.GenerativeModel(
            model_name=target_model,
            system_instruction=request.system_instruction
        )
        
        response = gen_model.generate_content(request.prompt, generation_config=generation_config)
        latency_ms = int((time.time() - start_time) * 1000)

        # Extract real token usage from Gemini response if available
        prompt_tokens = 0
        completion_tokens = 0
        is_estimated = True

        if hasattr(response, "usage_metadata") and response.usage_metadata:
            prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
            is_estimated = False
        
        if prompt_tokens == 0:
            prompt_tokens = len(request.prompt.split()) + (len(request.system_instruction.split()) if request.system_instruction else 0)
        if completion_tokens == 0:
            completion_tokens = len(response.text.split())

        total_tokens = prompt_tokens + completion_tokens
        
        # Calculate cost
        pricing = self.PRICING.get(target_model, self.PRICING["default"])
        cost = (prompt_tokens * pricing["prompt"]) + (completion_tokens * pricing["completion"])

        return GatewayGenerateResponse(
            text=response.text,
            provider="gemini",
            model=target_model,
            usage=UsageMetadata(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=round(cost, 6),
                is_estimated=is_estimated
            ),
            latency_ms=latency_ms,
            is_mock=False,
            request_id=req_id
        )
