from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class MetricResult:
    metric_name: str
    score: float
    threshold: float
    passed: bool
    reasoning: str
    evaluation_model: str = "gemini-1.5-flash"
    status: str = "SUCCESS"  # SUCCESS, ERROR, NOT_APPLICABLE
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EvaluationMetric(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_threshold(self) -> float:
        pass

    @abstractmethod
    def evaluate(
        self,
        input_text: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        context_docs: Optional[List[str]] = None,
        threshold: Optional[float] = None
    ) -> MetricResult:
        pass
