import time
import threading
from typing import Dict, Tuple, Optional
from app.config.settings import settings

class RateLimitResult:
    def __init__(self, allowed: bool, retry_after_sec: float = 0.0, reason: Optional[str] = None):
        self.allowed = allowed
        self.retry_after_sec = retry_after_sec
        self.reason = reason

class GatewayRateLimiter:
    def __init__(
        self,
        requests_per_minute: Optional[int] = None,
        tokens_per_minute: Optional[int] = None
    ):
        self.rpm = requests_per_minute or settings.LLM_GATEWAY_RATE_LIMIT_RPM
        self.tpm = tokens_per_minute or settings.LLM_GATEWAY_RATE_LIMIT_TPM
        self._lock = threading.Lock()
        # client_id -> list of (timestamp, token_count)
        self._client_history: Dict[str, list] = {}

    def check_and_record(self, client_id: str, estimated_tokens: int = 50) -> RateLimitResult:
        """
        Checks whether the client request is within RPM and TPM rate limits.
        If allowed, records the request timestamp.
        """
        now = time.time()
        window_start = now - 60.0  # 1-minute sliding window

        with self._lock:
            history = self._client_history.get(client_id, [])
            # Prune events older than 60 seconds
            history = [entry for entry in history if entry[0] > window_start]

            current_requests = len(history)
            current_tokens = sum(entry[1] for entry in history)

            if current_requests >= self.rpm:
                oldest_event_time = history[0][0]
                retry_after = round(max(0.1, 60.0 - (now - oldest_event_time)), 1)
                return RateLimitResult(
                    allowed=False,
                    retry_after_sec=retry_after,
                    reason=f"Rate limit exceeded: Max {self.rpm} requests/min reached."
                )

            if current_tokens + estimated_tokens > self.tpm:
                oldest_event_time = history[0][0]
                retry_after = round(max(0.1, 60.0 - (now - oldest_event_time)), 1)
                return RateLimitResult(
                    allowed=False,
                    retry_after_sec=retry_after,
                    reason=f"Token rate limit exceeded: Max {self.tpm} tokens/min reached."
                )

            # Record event
            history.append((now, estimated_tokens))
            self._client_history[client_id] = history
            return RateLimitResult(allowed=True)

    def reset(self):
        """Clears all in-memory rate limit records."""
        with self._lock:
            self._client_history.clear()

default_rate_limiter = GatewayRateLimiter()
