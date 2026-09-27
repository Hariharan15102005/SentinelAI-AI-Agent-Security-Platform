import re
from typing import Optional, Dict, Any, List
from app.guardrails.base import BaseGuardrail, GuardrailResult

class ToolSecurityGuardrail(BaseGuardrail):
    def __init__(self, allowed_tools: Optional[List[str]] = None, allow_readonly_db_only: bool = True):
        self.allowed_tools = allowed_tools or ["mock_database_query", "calculator", "controlled_document_search"]
        self.allow_readonly_db_only = allow_readonly_db_only

    @property
    def name(self) -> str:
        return "TOOL_EXECUTION_SECURITY_GATEWAY"

    # Dangerous patterns in tool arguments
    DANGEROUS_PATTERNS = {
        "SQL_WRITE_OR_DDL": re.compile(r"(?i)\b(DROP\s+TABLE|ALTER\s+TABLE|TRUNCATE\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|GRANT\s+ALL|REVOKE|SHUTDOWN)\b"),
        "SQL_EXPLOITATION": re.compile(r"(?i)(UNION\s+(?:ALL\s+)?SELECT|OR\s+1\s*=\s*1|SLEEP\s*\(\d+\)|BENCHMARK\s*\(|xp_cmdshell|LOAD_FILE|INTO\s+OUTFILE)"),
        "PATH_TRAVERSAL": re.compile(r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow|c:\\windows\\system32|windows/system32)"),
        "COMMAND_INJECTION": re.compile(r"(;|&&|\|\||`|\$\().*?(rm\s+-rf|curl|wget|bash|sh|powershell|cmd\.exe|nc\s+-e|cat\s+/etc/)"),
    }

    def validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> GuardrailResult:
        # 1. Whitelist validation
        if tool_name not in self.allowed_tools:
            return GuardrailResult(
                passed=False,
                rule_name=self.name,
                threat_type="UNAUTHORIZED_TOOL_INVOCATION",
                severity="CRITICAL",
                flagged_content=f"Requested tool '{tool_name}' is not in allowed sandbox tools: {self.allowed_tools}",
                action_taken="BLOCKED",
                confidence_score=1.0,
                reasoning=f"Attempted invocation of unauthorized tool: '{tool_name}'.",
                remediation_notes="Restrict agent execution to explicitly permitted tool namespaces."
            )

        # 2. Argument inspection for injection attacks
        raw_args_str = " ".join([str(v) for v in arguments.values()])

        for threat, pattern in self.DANGEROUS_PATTERNS.items():
            match = pattern.search(raw_args_str)
            if match:
                return GuardrailResult(
                    passed=False,
                    rule_name=self.name,
                    threat_type=threat,
                    severity="CRITICAL" if threat in ["SQL_WRITE_OR_DDL", "COMMAND_INJECTION"] else "HIGH",
                    flagged_content=f"Found suspicious payload in tool '{tool_name}' args: {match.group(0)}",
                    action_taken="BLOCKED",
                    confidence_score=0.98,
                    reasoning=f"Tool argument analysis flagged malicious pattern ({threat}) in parameters: {match.group(0)}.",
                    remediation_notes="Enforce strict parameterized queries, AST validation, and input sanitization before tool dispatch."
                )

        # 3. Readonly DB query check if tool is database query
        if tool_name == "mock_database_query" and self.allow_readonly_db_only:
            query = str(arguments.get("query", "")).strip().upper()
            if not query.startswith("SELECT") and not query.startswith("EXPLAIN") and not query.startswith("SHOW"):
                return GuardrailResult(
                    passed=False,
                    rule_name=self.name,
                    threat_type="NON_READONLY_DATABASE_OPERATION",
                    severity="HIGH",
                    flagged_content=f"Non-SELECT database query: {arguments.get('query')}",
                    action_taken="BLOCKED",
                    confidence_score=0.95,
                    reasoning="Database tool is constrained to read-only queries (SELECT/SHOW/EXPLAIN).",
                    remediation_notes="Configure database tool with read-only connection credentials and enforce query parsing."
                )

        return GuardrailResult(
            passed=True,
            rule_name=self.name,
            action_taken="PASSED"
        )
