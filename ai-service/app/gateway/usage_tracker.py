import threading
from typing import Dict, Any, List
from collections import deque
from app.gateway.types import GatewayUsageMetrics, UsageMetadata

class UsageTracker:
    MAX_AUDIT_LOG_SIZE = 100

    def __init__(self):
        self._lock = threading.Lock()
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._rate_limited_requests = 0
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost_usd = 0.0
        self._recent_logs = deque(maxlen=self.MAX_AUDIT_LOG_SIZE)

    def record_success(
        self,
        request_id: str,
        provider: str,
        model: str,
        usage: UsageMetadata,
        latency_ms: int
    ):
        with self._lock:
            self._total_requests += 1
            self._successful_requests += 1
            self._total_prompt_tokens += usage.prompt_tokens
            self._total_completion_tokens += usage.completion_tokens
            self._total_cost_usd += usage.estimated_cost_usd

            self._recent_logs.append({
                "requestId": request_id,
                "provider": provider,
                "model": model,
                "status": "SUCCESS",
                "promptTokens": usage.prompt_tokens,
                "completionTokens": usage.completion_tokens,
                "totalTokens": usage.total_tokens,
                "estimatedCostUsd": usage.estimated_cost_usd,
                "latencyMs": latency_ms
            })

    def record_failure(self, request_id: str, provider: str, model: str, error: str):
        with self._lock:
            self._total_requests += 1
            self._failed_requests += 1
            self._recent_logs.append({
                "requestId": request_id,
                "provider": provider,
                "model": model,
                "status": "FAILED",
                "error": error[:150]
            })

    def record_rate_limited(self, client_id: str):
        with self._lock:
            self._total_requests += 1
            self._rate_limited_requests += 1

    def get_metrics(self) -> GatewayUsageMetrics:
        with self._lock:
            return GatewayUsageMetrics(
                total_requests=self._total_requests,
                successful_requests=self._successful_requests,
                failed_requests=self._failed_requests,
                rate_limited_requests=self._rate_limited_requests,
                total_prompt_tokens=self._total_prompt_tokens,
                total_completion_tokens=self._total_completion_tokens,
                total_tokens=self._total_prompt_tokens + self._total_completion_tokens,
                total_estimated_cost_usd=round(self._total_cost_usd, 6)
            )

    def get_recent_logs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._recent_logs)

    def reset(self):
        with self._lock:
            self._total_requests = 0
            self._successful_requests = 0
            self._failed_requests = 0
            self._rate_limited_requests = 0
            self._total_prompt_tokens = 0
            self._total_completion_tokens = 0
            self._total_cost_usd = 0.0
            self._recent_logs.clear()

default_usage_tracker = UsageTracker()
