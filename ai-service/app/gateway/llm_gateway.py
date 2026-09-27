import time
import uuid
import logging
from typing import Dict, Any, List, Optional

from app.gateway.types import (
    GatewayGenerateRequest,
    GatewayGenerateResponse,
    ProviderModelInfo,
    GatewayModelsResponse,
    GatewayHealthResponse
)
from app.gateway.providers.base import BaseLLMProvider
from app.gateway.providers.gemini_provider import GeminiProvider
from app.gateway.providers.mock_provider import MockProvider
from app.gateway.rate_limiter import GatewayRateLimiter, default_rate_limiter
from app.gateway.usage_tracker import UsageTracker, default_usage_tracker
from app.config.settings import settings

logger = logging.getLogger(__name__)

class LLMGateway:
    def __init__(
        self,
        rate_limiter: Optional[GatewayRateLimiter] = None,
        usage_tracker: Optional[UsageTracker] = None
    ):
        self.rate_limiter = rate_limiter or default_rate_limiter
        self.usage_tracker = usage_tracker or default_usage_tracker
        self._providers: Dict[str, BaseLLMProvider] = {}
        
        # Register standard providers
        self.register_provider(GeminiProvider())
        self.register_provider(MockProvider())

    def register_provider(self, provider: BaseLLMProvider):
        """Registers an LLM provider adapter into the gateway."""
        self._providers[provider.provider_name] = provider
        logger.info(f"LLMGateway: Registered provider '{provider.provider_name}'")

    def get_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        return self._providers.get(provider_name)

    def list_available_models(self) -> GatewayModelsResponse:
        """Returns catalog of registered providers and supported models."""
        provider_infos: List[ProviderModelInfo] = []
        default_prov = settings.LLM_GATEWAY_DEFAULT_PROVIDER

        for name, prov in self._providers.items():
            provider_infos.append(ProviderModelInfo(
                provider=name,
                models=prov.get_supported_models(),
                is_available=prov.is_available(),
                is_default=(name == default_prov)
            ))

        return GatewayModelsResponse(
            providers=provider_infos,
            default_provider=default_prov,
            default_model=settings.DEFAULT_LLM_MODEL
        )

    def generate(self, request: GatewayGenerateRequest) -> GatewayGenerateResponse:
        """
        Validates, rate-limits, tracks, and executes text generation with retries.
        """
        # 1. Validation
        if not request.prompt or not request.prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if len(request.prompt) > 50000:
            raise ValueError("Prompt exceeds maximum allowed length of 50,000 characters.")

        client_id = request.client_id or "default_client"
        estimated_tokens = len(request.prompt.split()) + 20

        # 2. Rate Limiting
        rl_res = self.rate_limiter.check_and_record(client_id, estimated_tokens=estimated_tokens)
        if not rl_res.allowed:
            self.usage_tracker.record_rate_limited(client_id)
            raise PermissionError(f"RateLimitExceeded: {rl_res.reason} (Retry after {rl_res.retry_after_sec}s)")

        # 3. Provider Selection
        requested_provider_name = (request.provider or settings.LLM_GATEWAY_DEFAULT_PROVIDER).lower()
        provider = self.get_provider(requested_provider_name)

        if not provider:
            raise ValueError(f"Unsupported LLM provider '{requested_provider_name}'. Registered providers: {list(self._providers.keys())}")

        # If live provider is not configured or mock mode active, route to mock provider safely
        if not provider.is_available():
            logger.info(f"Provider '{requested_provider_name}' not available. Routing through mock provider.")
            provider = self._providers.get("mock", provider)

        # 4. Bounded Retry Loop with Exponential Backoff
        max_retries = settings.LLM_GATEWAY_MAX_RETRIES
        last_error = None
        req_id = f"gw_{uuid.uuid4().hex[:10]}"

        for attempt in range(max_retries):
            try:
                response = provider.generate(request)
                # 5. Record Usage Metrics
                self.usage_tracker.record_success(
                    request_id=response.request_id or req_id,
                    provider=response.provider,
                    model=response.model,
                    usage=response.usage,
                    latency_ms=response.latency_ms
                )
                return response
            except Exception as e:
                last_error = e
                logger.warning(f"LLMGateway attempt {attempt + 1}/{max_retries} failed on provider '{provider.provider_name}': {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff: 0.1s, 0.2s, 0.4s

        self.usage_tracker.record_failure(
            request_id=req_id,
            provider=provider.provider_name,
            model=request.model or "unknown",
            error=str(last_error)
        )
        raise RuntimeError(f"LLM Generation failed after {max_retries} attempts: {str(last_error)}")

    def get_health(self) -> GatewayHealthResponse:
        active_provs = [name for name, p in self._providers.items() if p.is_available()]
        metrics = self.usage_tracker.get_metrics()
        return GatewayHealthResponse(
            status="HEALTHY",
            active_providers=active_provs,
            default_provider=settings.LLM_GATEWAY_DEFAULT_PROVIDER,
            default_model=settings.DEFAULT_LLM_MODEL,
            rate_limiter_active=True,
            total_requests_processed=metrics.total_requests,
            total_tokens_processed=metrics.total_tokens
        )

default_llm_gateway = LLMGateway()
