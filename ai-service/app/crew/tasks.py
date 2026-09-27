import time
from typing import Dict, Any, List, Optional
from app.crew.types import (
    TargetSystemSpec,
    SecurityPlanTask,
    SecurityExecutionResult,
    CrewAssessmentReport,
    CrewAgentLog
)
from app.crew.agents import SecurityAnalystAgent, SecurityTesterAgent, SecurityReporterAgent

class ThreatAnalysisTask:
    """Task 1: Target system threat surface analysis and test planning."""
    def __init__(self, agent: SecurityAnalystAgent):
        self.agent = agent
        self.description = "Analyze the authorized target system architecture and generate an adversarial security testing plan."
        self.expected_output = "Structured list of SecurityPlanTask items covering requested risk domains."

    def run(
        self,
        target: TargetSystemSpec,
        requested_categories: List[str],
        custom_rules: Optional[List[str]] = None,
        audit_trail: Optional[List[CrewAgentLog]] = None
    ) -> List[SecurityPlanTask]:
        audit_trail = audit_trail if audit_trail is not None else []
        audit_trail.append(self.agent.log_action(
            action="THREAT_ANALYSIS_STARTED",
            details={"target_name": target.target_name, "categories": requested_categories}
        ))
        
        plan = self.agent.plan_security_tests(
            target=target,
            requested_categories=requested_categories,
            custom_rules=custom_rules
        )
        
        audit_trail.append(self.agent.log_action(
            action="THREAT_ANALYSIS_COMPLETED",
            details={"tasks_planned": len(plan), "task_ids": [t.task_id for t in plan]}
        ))
        return plan


class SecurityTestingTask:
    """Task 2: Execution of approved security tests against the target."""
    def __init__(self, agent: SecurityTesterAgent):
        self.agent = agent
        self.description = "Execute allowlisted security test payloads against the secured AI sandbox and collect empirical evidence."
        self.expected_output = "List of SecurityExecutionResult items detailing blocked attacks, vulnerabilities, and guardrail actions."

    def run(
        self,
        planned_tasks: List[SecurityPlanTask],
        target: TargetSystemSpec,
        execution_mode: str = "SECURED",
        max_iterations: int = 10,
        audit_trail: Optional[List[CrewAgentLog]] = None
    ) -> List[SecurityExecutionResult]:
        audit_trail = audit_trail if audit_trail is not None else []
        audit_trail.append(self.agent.log_action(
            action="SECURITY_TESTING_STARTED",
            details={"tasks_to_execute": min(len(planned_tasks), max_iterations), "mode": execution_mode}
        ))

        results: List[SecurityExecutionResult] = []
        for i, task in enumerate(planned_tasks):
            if i >= max_iterations:
                break
            res = self.agent.execute_test(task=task, target=target, execution_mode=execution_mode)
            results.append(res)

        audit_trail.append(self.agent.log_action(
            action="SECURITY_TESTING_COMPLETED",
            details={
                "tests_executed": len(results),
                "vulnerabilities_found": sum(1 for r in results if r.is_vulnerable),
                "attacks_blocked": sum(1 for r in results if r.is_blocked)
            }
        ))
        return results


class ReportGenerationTask:
    """Task 3: DeepEval scoring, risk aggregation, and security report authoring."""
    def __init__(self, agent: SecurityReporterAgent):
        self.agent = agent
        self.description = "Synthesize empirical results, compute DeepEval safety metrics, and author an executive security report."
        self.expected_output = "Complete CrewAssessmentReport instance."

    def run(
        self,
        target: TargetSystemSpec,
        execution_mode: str,
        planned_tasks: List[SecurityPlanTask],
        results: List[SecurityExecutionResult],
        audit_trail: Optional[List[CrewAgentLog]] = None,
        enable_eval_scoring: bool = True
    ) -> CrewAssessmentReport:
        audit_trail = audit_trail if audit_trail is not None else []
        audit_trail.append(self.agent.log_action(
            action="REPORT_SYNTHESIS_STARTED",
            details={"findings_to_evaluate": len(results)}
        ))

        report = self.agent.evaluate_and_generate_report(
            target=target,
            execution_mode=execution_mode,
            planned_tasks=planned_tasks,
            results=results,
            audit_trail=audit_trail,
            enable_eval_scoring=enable_eval_scoring
        )

        audit_trail.append(self.agent.log_action(
            action="REPORT_SYNTHESIS_COMPLETED",
            details={
                "assessment_id": report.assessment_id,
                "overall_risk_rating": report.overall_risk_rating,
                "total_findings": len(report.findings)
            }
        ))
        return report
