import time
from typing import Dict, Any, List, Optional
from app.crew.types import (
    TargetSystemSpec,
    CrewAssessmentRequest,
    CrewAssessmentReport,
    CrewAgentLog,
    SecurityPlanTask,
    SecurityExecutionResult
)
from app.crew.agents import (
    SecurityAnalystAgent,
    SecurityTesterAgent,
    SecurityReporterAgent
)
from app.crew.tasks import (
    ThreatAnalysisTask,
    SecurityTestingTask,
    ReportGenerationTask
)

class SentinelSecurityCrew:
    """
    CrewAI Multi-Agent Security Testing and Evaluation Orchestrator.
    Coordinates SecurityAnalystAgent, SecurityTesterAgent, and SecurityReporterAgent
    in a strictly bounded, observable, and sequential workflow.
    """
    def __init__(
        self,
        analyst_agent: Optional[SecurityAnalystAgent] = None,
        tester_agent: Optional[SecurityTesterAgent] = None,
        reporter_agent: Optional[SecurityReporterAgent] = None,
        process: str = "sequential",
        verbose: bool = True
    ):
        self.analyst = analyst_agent or SecurityAnalystAgent(verbose=verbose)
        self.tester = tester_agent or SecurityTesterAgent(verbose=verbose)
        self.reporter = reporter_agent or SecurityReporterAgent(verbose=verbose)
        self.process = process
        self.verbose = verbose

    def kickoff(self, request: CrewAssessmentRequest) -> CrewAssessmentReport:
        """
        Executes the multi-agent security assessment workflow across all 8 controlled stages.
        """
        start_time = time.time()
        audit_trail: List[CrewAgentLog] = []

        # Stage 1: Validate request and confirm authorization
        audit_trail.append(CrewAgentLog(
            agent_name="SentinelSecurityCrew",
            role="Orchestrator",
            action="WORKFLOW_INITIALIZED",
            timestamp=start_time,
            details={
                "target_name": request.target.target_name,
                "execution_mode": request.execution_mode,
                "categories": request.test_categories
            }
        ))

        # Stage 2 & 3: Threat analysis & security test planning
        threat_task = ThreatAnalysisTask(agent=self.analyst)
        planned_tasks: List[SecurityPlanTask] = threat_task.run(
            target=request.target,
            requested_categories=request.test_categories,
            custom_rules=request.custom_rules,
            audit_trail=audit_trail
        )

        # Stage 4 & 5: Security testing execution & empirical evidence collection
        testing_task = SecurityTestingTask(agent=self.tester)
        results: List[SecurityExecutionResult] = testing_task.run(
            planned_tasks=planned_tasks,
            target=request.target,
            execution_mode=request.execution_mode,
            max_iterations=request.max_iterations,
            audit_trail=audit_trail
        )

        # Stage 6 & 7: DeepEval evaluation, risk scoring, and report generation
        reporting_task = ReportGenerationTask(agent=self.reporter)
        report: CrewAssessmentReport = reporting_task.run(
            target=request.target,
            execution_mode=request.execution_mode,
            planned_tasks=planned_tasks,
            results=results,
            audit_trail=audit_trail,
            enable_eval_scoring=request.enable_eval_scoring
        )

        # Stage 8: Return report and metadata
        total_time_ms = int((time.time() - start_time) * 1000)
        report.total_duration_ms = total_time_ms
        report.formatted_date = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        audit_trail.append(CrewAgentLog(
            agent_name="SentinelSecurityCrew",
            role="Orchestrator",
            action="WORKFLOW_COMPLETED",
            timestamp=time.time(),
            details={
                "assessment_id": report.assessment_id,
                "duration_ms": total_time_ms,
                "overall_risk_rating": report.overall_risk_rating
            }
        ))
        report.agent_audit_trail = audit_trail

        return report
