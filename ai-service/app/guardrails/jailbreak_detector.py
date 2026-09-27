import re
import base64
from typing import Optional, Dict, Any
from app.guardrails.base import BaseGuardrail, GuardrailResult

class JailbreakGuardrail(BaseGuardrail):
    @property
    def name(self) -> str:
        return "JAILBREAK_DETECTOR"

    # Known Persona and Roleplay Hijacking Signatures
    PERSONA_PATTERNS = [
        (r"\byou\s+are\s+now\s+(in\s+)?(dan|do\s+anything\s+now)\b", 0.96, "PERSONA_HIJACKING_DAN", "Persona Hijacking (DAN Mode)"),
        (r"\b(simulate\s+)?developer\s+mode(\s+enabled)?\b|\bdeveloper\s+mode\b", 0.95, "DEVELOPER_MODE_BYPASS", "Developer Mode Bypass"),
        (r"\byou\s+are\s+now\s+(in\s+)?(evil\s+twin|maximum|god\s+mode|unfiltered\s+mode|opposites\s+mode)\b", 0.92, "JAILBREAK_PERSONA_OVERRIDE", "Unfiltered Persona Hijacking"),
        (r"\bfrom\s+now\s+on\s+you\s+(will\s+|must\s+)?act\s+as\s+(an\s+unfiltered|an\s+evil|a\s+rogue|a\s+lawless)\b", 0.90, "UNFILTERED_ROLEPLAY", "Unfiltered Agent Roleplay"),
        (r"\bdisregard\s+(all\s+)?(ethical|safety|legal)\s+(protocols|guidelines|policies)\b", 0.95, "SAFETY_PROTOCOL_OVERRIDE", "Safety Protocol Override"),
        (r"\bpretend\s+you\s+have\s+no\s+safety\s+(filters|rules|constraints)\b", 0.90, "FILTER_BYPASS_SIMULATION", "Safety Filter Bypass Simulation"),
        (r"\byou\s+are\s+an\s+ai\s+without\s+any\s+restrictions\s+or\s+filters\b", 0.92, "RESTRICTION_REMOVAL_CLAIM", "Constraint Removal Claim")
    ]

    # Hypothetical Adversarial Framing
    HYPOTHETICAL_ADVERSARIAL_PATTERNS = [
        (r"\b(hypothetically\s+speaking|purely\s+for\s+academic|in\s+a\s+(hypothetical|fictional)\s+(scenario|universe)).*?(how\s+would\s+one\s+bypass|bypass\s+corporate\s+ai|hack|steal|safety\s+is\s+illegal)\b", 0.88, "HYPOTHETICAL_ADVERSARIAL_FRAMING", "Hypothetical Lawless World Framing"),
        (r"\bwrite\s+a\s+story\s+where\s+a\s+hacker\s+successfully\s+steals\s+passwords\s+by\s+doing:\b", 0.88, "MALICIOUS_STORYTELLING", "Instructional Malicious Storytelling")
    ]

    # General adversarial patterns to test inside decoded Base64 or obfuscated text
    SUSPICIOUS_PAYLOAD_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"reveal\s+all\s+secrets",
        r"system\s+prompt",
        r"dan|developer\s+mode",
        r"bypass\s+safety"
    ]

    def validate_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        if not text:
            return GuardrailResult(passed=True, rule_name=self.name)

        text_clean = text.strip()

        # 1. Check Persona Hijacking
        for pattern, conf, threat_type, desc in self.PERSONA_PATTERNS:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                return GuardrailResult(
                    passed=False,
                    rule_name=self.name,
                    threat_type=threat_type,
                    severity="CRITICAL" if "DAN" in threat_type or "DEVELOPER" in threat_type else "HIGH",
                    flagged_content=match.group(0),
                    action_taken="BLOCKED",
                    confidence_score=conf,
                    reasoning=f"Jailbreak signature identified: {desc}.",
                    remediation_notes="Implement system prompt role anchoring and multi-turn persona verification."
                )

        # 2. Check Hypothetical Framing
        for pattern, conf, threat_type, desc in self.HYPOTHETICAL_ADVERSARIAL_PATTERNS:
            match = re.search(pattern, text_clean, re.IGNORECASE | re.DOTALL)
            if match:
                return GuardrailResult(
                    passed=False,
                    rule_name=self.name,
                    threat_type=threat_type,
                    severity="HIGH",
                    flagged_content=match.group(0)[:80],
                    action_taken="BLOCKED",
                    confidence_score=conf,
                    reasoning=f"Adversarial jailbreak framing identified: {desc}.",
                    remediation_notes="Constrain agent to legitimate business roles and reject adversarial hypothetical preambles."
                )

        # 3. Check for Suspicious Encoded Payloads (e.g. Base64 strings)
        b64_matches = re.findall(r"\b[A-Za-z0-9+/]{20,}={0,2}\b", text_clean)
        for candidate in b64_matches:
            try:
                decoded = base64.b64decode(candidate).decode('utf-8', errors='ignore')
                for sp_pattern in self.SUSPICIOUS_PAYLOAD_PATTERNS:
                    if re.search(sp_pattern, decoded, re.IGNORECASE):
                        return GuardrailResult(
                            passed=False,
                            rule_name=self.name,
                            threat_type="BASE64_OBFUSCATED_JAILBREAK",
                            severity="CRITICAL",
                            flagged_content=f"Base64 Encoded Payload: {candidate[:20]}... (Decoded: '{decoded[:50]}')",
                            action_taken="BLOCKED",
                            confidence_score=0.98,
                            reasoning=f"Obfuscated jailbreak payload detected inside encoded string: '{decoded[:40]}...'",
                            remediation_notes="Decode and scan base64 and hex strings before passing into LLM context."
                        )
            except Exception:
                pass

        return GuardrailResult(passed=True, rule_name=self.name, action_taken="PASSED", confidence_score=1.0)

# Backward-compatibility alias
JailbreakDetectorGuardrail = JailbreakGuardrail
