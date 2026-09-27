from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.gateway.types import GatewayGenerateRequest, GatewayGenerateResponse

class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique identifier for the provider (e.g. 'gemini', 'mock')."""
        pass

    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Returns list of approved model identifiers for this provider."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if provider has required credentials and configuration."""
        pass

    @abstractmethod
    def generate(self, request: GatewayGenerateRequest) -> GatewayGenerateResponse:
        """Executes text generation against the provider with usage metadata tracking."""
        pass
