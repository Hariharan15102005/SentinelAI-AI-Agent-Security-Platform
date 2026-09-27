import re
from typing import Optional, Dict, Any, List, Tuple
from app.guardrails.base import BaseGuardrail, GuardrailResult

def luhn_checksum(card_num_str: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", card_num_str)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += d
    return checksum % 10 == 0

class PIIAnonymizerGuardrail(BaseGuardrail):
    def __init__(self, mask_in_place: bool = True, block_on_critical_pii: bool = False):
        self.mask_in_place = mask_in_place
        self.block_on_critical_pii = block_on_critical_pii

    @property
    def name(self) -> str:
        return "PII_AND_SECRETS_DETECTOR"

    # Regex patterns for various sensitive data types
    PATTERNS = {
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
        "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "PHONE": re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b"),
        "API_KEY": re.compile(
            r"(?i)\b(?:sk-[a-zA-Z0-9_-]{20,}|AIza[0-9A-Za-z-_]{35}|ghp_[a-zA-Z0-9]{36}|AKIA[0-9A-Z]{16}|bearer\s+[a-zA-Z0-9\-._~+/]+=*)\b"
        ),
        "CREDIT_CARD_CANDIDATE": re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b|\b\d{15,16}\b")
    }

    def _scan_and_mask(self, text: str) -> Tuple[List[Dict[str, Any]], str]:
        findings = []
        sanitized_text = text

        # 1. API Keys & Secrets (CRITICAL)
        for match in self.PATTERNS["API_KEY"].finditer(text):
            secret_val = match.group(0)
            findings.append({
                "type": "EXPOSED_API_KEY_OR_SECRET",
                "severity": "CRITICAL",
                "match": secret_val[:6] + "..." + secret_val[-3:] if len(secret_val) > 9 else "[SECRET]",
                "raw_match": secret_val
            })
            sanitized_text = sanitized_text.replace(secret_val, "[REDACTED_SECRET]")

        # 2. SSN (HIGH)
        for match in self.PATTERNS["SSN"].finditer(text):
            ssn_val = match.group(0)
            findings.append({
                "type": "PII_SSN",
                "severity": "HIGH",
                "match": ssn_val,
                "raw_match": ssn_val
            })
            sanitized_text = sanitized_text.replace(ssn_val, "[REDACTED_SSN]")

        # 3. Credit Cards (HIGH)
        for match in self.PATTERNS["CREDIT_CARD_CANDIDATE"].finditer(text):
            cc_val = match.group(0)
            clean_digits = re.sub(r"\D", "", cc_val)
            if luhn_checksum(clean_digits):
                findings.append({
                    "type": "PII_CREDIT_CARD",
                    "severity": "HIGH",
                    "match": f"****-****-****-{clean_digits[-4:]}",
                    "raw_match": cc_val
                })
                sanitized_text = sanitized_text.replace(cc_val, "[REDACTED_CREDIT_CARD]")

        # 4. Email (MEDIUM)
        for match in self.PATTERNS["EMAIL"].finditer(text):
            email_val = match.group(0)
            # Avoid replacing already redacted token placeholders
            if "REDACTED" not in email_val:
                findings.append({
                    "type": "PII_EMAIL",
                    "severity": "MEDIUM",
                    "match": email_val,
                    "raw_match": email_val
                })
                sanitized_text = sanitized_text.replace(email_val, "[REDACTED_EMAIL]")

        # 5. Phone numbers (LOW/MEDIUM)
        for match in self.PATTERNS["PHONE"].finditer(text):
            phone_val = match.group(0)
            # Exclude short digit sequences or common dates
            if len(re.sub(r"\D", "", phone_val)) >= 10:
                findings.append({
                    "type": "PII_PHONE_NUMBER",
                    "severity": "MEDIUM",
                    "match": phone_val,
                    "raw_match": phone_val
                })
                sanitized_text = sanitized_text.replace(phone_val, "[REDACTED_PHONE]")

        return findings, sanitized_text

    def validate_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        findings, sanitized = self._scan_and_mask(text)
        if not findings:
            return GuardrailResult(passed=True, rule_name=self.name)

        has_critical = any(f["severity"] in ["CRITICAL", "HIGH"] for f in findings)
        finding_types = list(set(f["type"] for f in findings))

        should_block = self.block_on_critical_pii and has_critical
        action = "BLOCKED" if should_block else ("MASKED" if self.mask_in_place else "FLAGGED_ONLY")
        
        return GuardrailResult(
            passed=not should_block,
            rule_name=self.name,
            threat_type=finding_types[0] if len(finding_types) == 1 else "MULTIPLE_SENSITIVE_DATA_EXPOSURES",
            severity="CRITICAL" if has_critical else "MEDIUM",
            flagged_content=", ".join(f"{f['type']}: {f['match']}" for f in findings),
            action_taken=action,
            confidence_score=0.95,
            reasoning=f"Detected sensitive data exposure ({len(findings)} items found: {', '.join(finding_types)}).",
            remediation_notes="Anonymize or strip PII/credentials before passing to AI models.",
            sanitized_content=sanitized if self.mask_in_place else text
        )

    def validate_output(self, text: str, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        findings, sanitized = self._scan_and_mask(text)
        if not findings:
            return GuardrailResult(passed=True, rule_name=self.name)

        has_critical = any(f["severity"] in ["CRITICAL", "HIGH"] for f in findings)
        finding_types = list(set(f["type"] for f in findings))

        # Model output containing raw credentials or SSN is dangerous
        action = "MASKED" if self.mask_in_place else "FLAGGED_ONLY"
        
        return GuardrailResult(
            passed=True,  # Output can be sanitized in place
            rule_name=self.name,
            threat_type="MODEL_SENSITIVE_DATA_LEAKAGE",
            severity="HIGH" if has_critical else "MEDIUM",
            flagged_content=", ".join(f"{f['type']}: {f['match']}" for f in findings),
            action_taken=action,
            confidence_score=0.95,
            reasoning=f"Agent generated output containing potentially sensitive information ({', '.join(finding_types)}).",
            remediation_notes="Sanitize model outputs and audit prompt history for sensitive training or context data.",
            sanitized_content=sanitized
        )
