import re
from typing import Optional, Dict, Any
from app.guardrails.base import BaseGuardrail, GuardrailResult

class PromptInjectionGuardrail(BaseGuardrail):
    @property
    def name(self) -> str:
        return "PROMPT_INJECTION_DETECTOR"

    # Pattern definitions with specific threat types
    PATTERNS = [
        # Direct instruction overrides
        (r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|rules|constraints|format\s+requirements)\b", 0.95, "DIRECT_INSTRUCTION_OVERRIDE", "Direct Instruction Override"),
        (r"(?i)\bforget\s+(all\s+)?(your\s+)?(rules|instructions|system\s+prompt)\b", 0.90, "DIRECT_INSTRUCTION_OVERRIDE", "Instruction Erasure Attempt"),
        (r"(?i)\bnew\s+operating\s+instructions\b|\byou\s+must\s+now\s+follow\s+these\s+new\s+rules\b", 0.85, "DIRECT_INSTRUCTION_OVERRIDE", "Rule Hijacking"),
        
        # System prompt extraction
        (r"(?i)\b(print|output|display|show|reveal|repeat)\s+(your\s+)?(?:full\s+|initial\s+|complete\s+|original\s+|system\s+)*(system\s+prompt|developer\s+instructions|system\s+directives|hidden\s+constraints)\b", 0.95, "SYSTEM_PROMPT_EXTRACTION", "System Prompt Extraction"),
        (r"(?i)\bwhat\s+were\s+your\s+(initial|first|original)\s+instructions\s+verbatim\b", 0.90, "SYSTEM_PROMPT_EXTRACTION", "Verbatim Prompt Extraction"),
        (r"(?i)\breproduce\s+(the\s+)?text\s+above\s+starting\s+with\s+you\s+are\b", 0.85, "SYSTEM_PROMPT_EXTRACTION", "System Directive Leakage Attempt"),
        
        # Delimiter & Structured Injection Attacks
        (r"(<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>|\[SYSTEM:\s*OVERRIDE\s*ACTIVE\])", 0.95, "DELIMITER_INJECTION_ATTACK", "Special Token / Delimiter Injection"),
        (r"(?i)---+\s*(END\s+OF\s+SYSTEM|START\s+OF\s+ADMIN|SYSTEM\s+OVERRIDE)\s*---+", 0.95, "DELIMITER_INJECTION_ATTACK", "Delimiter Bypass Attack"),
        (r"(?i)```(system|admin|root|override)", 0.90, "DELIMITER_INJECTION_ATTACK", "Fake System Role Delimiter")
    ]

    def validate_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        if not text:
            return GuardrailResult(passed=True, rule_name=self.name)

        text_clean = text.strip()

        for pattern, confidence, threat_type, threat_desc in self.PATTERNS:
            match = re.search(pattern, text_clean)
            if match:
                flagged_snippet = match.group(0)
                return GuardrailResult(
                    passed=False,
                    rule_name=self.name,
                    threat_type=threat_type,
                    severity="HIGH",
                    flagged_content=flagged_snippet,
                    action_taken="BLOCKED",
                    confidence_score=confidence,
                    reasoning=f"Adversarial prompt injection pattern detected: '{threat_desc}'.",
                    remediation_notes="Anchor system instructions in developer message roles and enforce input token boundary verification."
                )

        return GuardrailResult(
            passed=True,
            rule_name=self.name,
            action_taken="PASSED",
            confidence_score=1.0
        )
