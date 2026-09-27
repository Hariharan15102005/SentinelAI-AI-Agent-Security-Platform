from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class UsageMetadata(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    is_estimated: bool = True

class GatewayGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=50000, description="Prompt text to send to LLM")
    system_instruction: Optional[str] = None
    provider: Optional[str] = "gemini"
    model: Optional[str] = "gemini-1.5-flash"
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=2.0)
    max_output_tokens: Optional[int] = Field(default=1000, ge=1, le=8192)
    client_id: Optional[str] = "default_client"
    trace_id: Optional[str] = None

class GatewayGenerateResponse(BaseModel):
    text: str
    provider: str
    model: str
    usage: UsageMetadata
    latency_ms: int
    is_mock: bool = False
    request_id: str

class ProviderModelInfo(BaseModel):
    provider: str
    models: List[str]
    is_available: bool
    is_default: bool = False

class GatewayModelsResponse(BaseModel):
    providers: List[ProviderModelInfo]
    default_provider: str
    default_model: str

class GatewayUsageMetrics(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limited_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_estimated_cost_usd: float

class GatewayHealthResponse(BaseModel):
    status: str = "HEALTHY"
    active_providers: List[str]
    default_provider: str
    default_model: str
    rate_limiter_active: bool
    total_requests_processed: int
    total_tokens_processed: int
