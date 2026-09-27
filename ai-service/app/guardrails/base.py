from dataclasses import dataclass
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class GuardrailResult:
    passed: bool
    rule_name: str
    threat_type: Optional[str] = None
    severity: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    flagged_content: Optional[str] = None
    action_taken: str = "PASSED"  # BLOCKED, MASKED, FLAGGED_ONLY, PASSED
    confidence_score: float = 1.0
    reasoning: Optional[str] = None
    remediation_notes: Optional[str] = None
    sanitized_content: Optional[str] = None

class BaseGuardrail(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def validate_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        return GuardrailResult(passed=True, rule_name=self.name)

    def validate_output(self, text: str, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        return GuardrailResult(passed=True, rule_name=self.name)
