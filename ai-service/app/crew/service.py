import time
from typing import Dict, Any, List, Optional
from app.crew.types import (
    CrewAssessmentRequest,
    CrewAssessmentReport
)
from app.crew.crew import SentinelSecurityCrew

class CrewWorkflowService:
    """
    Service layer providing unified access, execution, and in-memory registry for CrewAI assessments.
    """
    def __init__(self):
        self._crew = SentinelSecurityCrew()
        self._reports_db: Dict[str, CrewAssessmentReport] = {}

    def execute_assessment(self, request: CrewAssessmentRequest) -> CrewAssessmentReport:
        """Executes a security assessment and registers the generated report."""
        report = self._crew.kickoff(request)
        self._reports_db[report.assessment_id] = report
        return report

    def get_report(self, assessment_id: str) -> Optional[CrewAssessmentReport]:
        """Retrieves a previously generated assessment report by ID."""
        return self._reports_db.get(assessment_id)

    def list_reports(self) -> List[Dict[str, Any]]:
        """Lists summaries of all completed assessments."""
        summaries = []
        for r in self._reports_db.values():
            summaries.append({
                "assessment_id": r.assessment_id,
                "target_name": r.target_name,
                "execution_mode": r.execution_mode,
                "status": r.status,
                "overall_risk_rating": r.overall_risk_rating,
                "tests_executed": r.tests_executed,
                "tests_passed": r.tests_passed,
                "findings_count": len(r.findings),
                "timestamp": r.timestamp,
                "formatted_date": r.formatted_date
            })
        return summaries

default_crew_service = CrewWorkflowService()
