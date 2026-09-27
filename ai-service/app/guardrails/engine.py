import logging
from typing import List, Dict, Any, Optional, Tuple
from app.guardrails.base import BaseGuardrail, GuardrailResult
from app.guardrails.prompt_injection import PromptInjectionGuardrail
from app.guardrails.jailbreak_detector import JailbreakGuardrail
from app.guardrails.pii_anonymizer import PIIAnonymizerGuardrail
from app.guardrails.tool_security import ToolSecurityGuardrail

logger = logging.getLogger("sentinelai.guardrails")

class GuardrailsEngine:
    def __init__(
        self,
        enable_prompt_injection: bool = True,
        enable_jailbreak: bool = True,
        enable_pii_masking: bool = True,
        enable_tool_security: bool = True,
        block_on_critical: bool = True
    ):
        self.enable_prompt_injection = enable_prompt_injection
        self.enable_jailbreak = enable_jailbreak
        self.enable_pii_masking = enable_pii_masking
        self.enable_tool_security = enable_tool_security
        self.block_on_critical = block_on_critical

        self.input_guardrails: List[BaseGuardrail] = []
        self.output_guardrails: List[BaseGuardrail] = []

        if self.enable_prompt_injection:
            self.input_guardrails.append(PromptInjectionGuardrail())

        if self.enable_jailbreak:
            self.input_guardrails.append(JailbreakGuardrail())

        if self.enable_pii_masking:
            pii_guard = PIIAnonymizerGuardrail(mask_in_place=True, block_on_critical_pii=block_on_critical)
            self.input_guardrails.append(pii_guard)
            self.output_guardrails.append(pii_guard)

        self.tool_security_guard = ToolSecurityGuardrail() if self.enable_tool_security else None

    def scan_input(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Tuple[List[GuardrailResult], bool, str]:
        """
        Scans input prompt against all registered input guardrails.
        Returns:
            (findings, should_block, sanitized_prompt)
        """
        findings: List[GuardrailResult] = []
        should_block = False
        current_prompt = prompt

        for guard in self.input_guardrails:
            try:
                res = guard.validate_input(current_prompt, context=context)
                if not res.passed or res.threat_type is not None:
                    findings.append(res)
                    if not res.passed or res.action_taken == "BLOCKED":
                        should_block = True
                    if res.sanitized_content is not None:
                        current_prompt = res.sanitized_content
            except Exception as e:
                logger.error(f"Error executing guardrail {guard.name}: {str(e)}", exc_info=True)
                findings.append(GuardrailResult(
                    passed=False,
                    rule_name=guard.name,
                    threat_type="GUARDRAIL_EXECUTION_ERROR",
                    severity="MEDIUM",
                    flagged_content=str(e),
                    action_taken="FLAGGED_ONLY",
                    confidence_score=0.5,
                    reasoning=f"Guardrail execution failed due to an internal error: {str(e)}"
                ))

        return findings, should_block, current_prompt

    def scan_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Optional[GuardrailResult], bool]:
        """
        Scans tool invocation parameters.
        Returns:
            (result, should_block)
        """
        if not self.tool_security_guard:
            return None, False

        try:
            res = self.tool_security_guard.validate_tool_call(tool_name, arguments)
            if not res.passed or res.action_taken == "BLOCKED":
                return res, True
            return res, False
        except Exception as e:
            logger.error(f"Error validating tool call {tool_name}: {str(e)}", exc_info=True)
            return GuardrailResult(
                passed=False,
                rule_name="TOOL_EXECUTION_SECURITY_GATEWAY",
                threat_type="TOOL_VALIDATION_ERROR",
                severity="HIGH",
                flagged_content=str(e),
                action_taken="BLOCKED",
                confidence_score=0.5,
                reasoning=f"Failed to validate tool call: {str(e)}"
            ), True

    def scan_output(self, response_text: str, context: Optional[Dict[str, Any]] = None) -> Tuple[List[GuardrailResult], str]:
        """
        Scans output text and performs sanitization.
        Returns:
            (findings, sanitized_response)
        """
        findings: List[GuardrailResult] = []
        current_text = response_text

        for guard in self.output_guardrails:
            try:
                res = guard.validate_output(current_text, context=context)
                if not res.passed or res.threat_type is not None:
                    findings.append(res)
                    if res.sanitized_content is not None:
                        current_text = res.sanitized_content
            except Exception as e:
                logger.error(f"Error executing output guardrail {guard.name}: {str(e)}", exc_info=True)

        return findings, current_text

    @staticmethod
    def map_threat_to_category(threat_type: Optional[str]) -> str:
        if not threat_type:
            return "GENERAL_SECURITY_VIOLATION"
        tt = threat_type.upper()
        if "PROMPT_INJECTION" in tt or "SYSTEM_PROMPT" in tt or "DELIMITER" in tt:
            return "PROMPT_INJECTION"
        if "JAILBREAK" in tt or "PERSONA" in tt or "BASE64" in tt:
            return "JAILBREAK"
        if "PII" in tt or "SECRET" in tt or "CREDIT_CARD" in tt or "SSN" in tt or "LEAKAGE" in tt:
            return "SENSITIVE_DATA_EXPOSURE"
        if "TOOL" in tt or "SQL" in tt or "PATH_TRAVERSAL" in tt or "COMMAND" in tt:
            return "UNAUTHORIZED_TOOL_USE"
        return "POLICY_VIOLATION"

    def convert_to_security_findings(
        self,
        guardrail_results: List[GuardrailResult],
        phase: str = "INPUT"
    ) -> List[Dict[str, Any]]:
        findings = []
        for res in guardrail_results:
            findings.append({
                "category": self.map_threat_to_category(res.threat_type),
                "severity": res.severity,
                "detectionSource": "GUARDRAILS_AI",
                "triggeredControl": res.rule_name,
                "evidence": res.flagged_content or res.reasoning or f"Violated {res.rule_name}",
                "remediation": res.remediation_notes or "Review and strengthen agent safety parameters.",
                "blocked": res.action_taken == "BLOCKED" or not res.passed,
                "confidenceScore": res.confidence_score,
                "metadata": {
                    "phase": phase,
                    "threatType": res.threat_type,
                    "actionTaken": res.action_taken
                }
            })
        return findings

default_guardrails_engine = GuardrailsEngine()
