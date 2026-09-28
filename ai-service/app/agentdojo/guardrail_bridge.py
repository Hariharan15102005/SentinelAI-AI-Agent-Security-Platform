import re
import logging
from typing import List, Dict, Any, Optional, Tuple

from app.guardrails.engine import GuardrailsEngine
from app.guardrails.base import GuardrailResult

logger = logging.getLogger("sentinelai.agentdojo.bridge")

class SentinelAIGuardrailBridge:
    """
    Connects SentinelAI's multi-layered Guardrails AI defense engine
    to the AgentDojo benchmark execution cycle.
    """

    def __init__(
        self,
        active_guardrails: Optional[List[str]] = None,
        block_on_critical: bool = True
    ):
        self.active_guardrails = active_guardrails or [
            "PromptInjectionDetector",
            "PIIAnonymizer",
            "SQLInjectionGuard"
        ]
        self.block_on_critical = block_on_critical

        enable_prompt = "PromptInjectionDetector" in self.active_guardrails
        enable_jailbreak = "PromptInjectionDetector" in self.active_guardrails or "JailbreakDetector" in self.active_guardrails
        enable_pii = "PIIAnonymizer" in self.active_guardrails
        enable_tool = "SQLInjectionGuard" in self.active_guardrails or "ToolSecurityGuard" in self.active_guardrails

        self.engine = GuardrailsEngine(
            enable_prompt_injection=enable_prompt,
            enable_jailbreak=enable_jailbreak,
            enable_pii_masking=enable_pii,
            enable_tool_security=enable_tool,
            block_on_critical=block_on_critical
        )

    def scan_user_prompt(self, prompt: str) -> Tuple[List[GuardrailResult], bool, str]:
        """Scans the initial user prompt."""
        return self.engine.scan_input(prompt)

    def scan_tool_invocation(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Optional[GuardrailResult], bool]:
        """Validates tool execution parameters (e.g., unauthorized SQL or system command strings)."""
        return self.engine.scan_tool_call(tool_name, arguments)

    def scan_tool_output(self, tool_name: str, output: str) -> Tuple[List[GuardrailResult], bool, str]:
        """
        Crucial for AgentDojo: Scans tool return values (emails, files, database records)
        for indirect prompt injections and embedded attack directives.
        """
        findings: List[GuardrailResult] = []
        should_block = False
        sanitized_output = output

        # 1. Check for indirect prompt injection signatures in untrusted tool data
        indirect_injection_patterns = [
            r"ignore\s+(previous|prior|above)\s+instructions",
            r"important\s+instructions?\s*:",
            r"system\s*override\s*:",
            r"new\s+task\s*:",
            r"forward\s+all\s+(emails|contacts|messages)",
            r"send\s+(money|funds|balance|payment)\s+to",
            r"transfer\s+\$?[0-9,]+(\.[0-9]{2})?\s+to",
            r"execute\s+tool\s*:",
            r"exfiltrate\s+to\s+https?://",
            r"do\s+not\s+tell\s+the\s+user",
            r"secret\s+command\s*:"
        ]

        if "PromptInjectionDetector" in self.active_guardrails and isinstance(output, str):
            for pattern in indirect_injection_patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    finding = GuardrailResult(
                        passed=False,
                        rule_name="INDIRECT_PROMPT_INJECTION_FILTER",
                        threat_type="INDIRECT_PROMPT_INJECTION",
                        severity="CRITICAL",
                        flagged_content=match.group(0),
                        action_taken="BLOCKED",
                        confidence_score=0.95,
                        reasoning=f"Detected embedded indirect prompt injection inside tool output from '{tool_name}'"
                    )
                    findings.append(finding)
                    should_block = True
                    break

        # 2. Check for PII leakage in tool output
        if "PIIAnonymizer" in self.active_guardrails and isinstance(output, str):
            pii_findings, masked_output = self.engine.scan_output(output)
            findings.extend(pii_findings)
            if any(not f.passed or f.action_taken == "BLOCKED" for f in pii_findings):
                should_block = True
            sanitized_output = masked_output

        return findings, should_block, sanitized_output
