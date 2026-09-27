package com.sentinelai.service;

import com.sentinelai.dto.response.DashboardSummaryResponse;
import com.sentinelai.dto.response.TestRunResponse;
import com.sentinelai.entity.Project;
import com.sentinelai.entity.TestRun;
import com.sentinelai.enums.ExecutionMode;
import com.sentinelai.exception.ResourceNotFoundException;
import com.sentinelai.exception.UnauthorizedAccessException;
import com.sentinelai.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class DashboardService {

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private TestRunRepository testRunRepository;

    @Autowired
    private SecurityFindingRepository securityFindingRepository;

    @Autowired
    private EvaluationResultRepository evaluationResultRepository;

    @Transactional(readOnly = true)
    public DashboardSummaryResponse getDashboardSummary(Long projectId, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found with id: " + projectId));

        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to access project: " + projectId);
        }

        DashboardSummaryResponse response = new DashboardSummaryResponse();

        long totalRuns = testRunRepository.countByProjectId(projectId);
        long findingsTotal = securityFindingRepository.countByProjectId(projectId);
        long vulnerableRuns = testRunRepository.countByProjectIdAndIsVulnerable(projectId, true);
        long securedRuns = testRunRepository.countByProjectIdAndExecutionMode(projectId, ExecutionMode.SECURED);

        Double avgLatency = testRunRepository.findAverageLatencyByProjectId(projectId);
        Double avgScore = testRunRepository.findAverageScoreByProjectId(projectId);

        response.setTotalRuns(totalRuns);
        response.setSecurityFindingsTotal(findingsTotal);
        response.setAverageLatencyMs(avgLatency != null ? Math.round(avgLatency * 10.0) / 10.0 : 0.0);
        response.setAverageFaithfulnessScore(avgScore != null ? Math.round((avgScore / 100.0) * 100.0) / 100.0 : 0.0);

        double passRate = totalRuns > 0 ? ((double) (totalRuns - vulnerableRuns) / totalRuns) * 100.0 : 0.0;
        response.setSecurityTestPassRate(Math.round(passRate * 10.0) / 10.0);
        response.setTaskSuccessRate(totalRuns > 0 ? Math.round(((double) (totalRuns - vulnerableRuns) / totalRuns * 100.0) * 10.0) / 10.0 : 0.0);
        response.setVulnerabilityRate(totalRuns > 0 ? Math.round(((double) vulnerableRuns / totalRuns * 100.0) * 10.0) / 10.0 : 0.0);
        response.setGuardrailMitigationRate(totalRuns > 0 ? Math.round(((double) securedRuns / totalRuns * 100.0) * 10.0) / 10.0 : 0.0);

        // Threat Distribution
        List<DashboardSummaryResponse.ThreatDistributionItem> threatDist = new ArrayList<>();
        List<Object[]> threatCounts = securityFindingRepository.countByThreatTypeForProject(projectId);
        for (Object[] row : threatCounts) {
            threatDist.add(new DashboardSummaryResponse.ThreatDistributionItem(row[0] != null ? row[0].toString() : "Unknown", (Long) row[1]));
        }
        response.setThreatDistribution(threatDist);

        // Severity Distribution
        List<DashboardSummaryResponse.SeverityDistributionItem> severityDist = new ArrayList<>();
        List<Object[]> severityCounts = securityFindingRepository.countBySeverityForProject(projectId);
        for (Object[] row : severityCounts) {
            String sevName = row[0] != null ? row[0].toString() : "LOW";
            Long count = (Long) row[1];
            String color = "#06b6d4";
            if ("CRITICAL".equalsIgnoreCase(sevName)) color = "#dc2626";
            else if ("HIGH".equalsIgnoreCase(sevName)) color = "#f97316";
            else if ("MEDIUM".equalsIgnoreCase(sevName)) color = "#eab308";
            else if ("LOW".equalsIgnoreCase(sevName)) color = "#06b6d4";
            severityDist.add(new DashboardSummaryResponse.SeverityDistributionItem(sevName, count, color));
        }
        response.setFindingsBySeverity(severityDist);

        // Recent Runs
        List<TestRun> recent = testRunRepository.findTop5ByProjectIdOrderByCreatedAtDesc(projectId);
        List<TestRunResponse> recentResponses = recent.stream().map(r -> {
            TestRunResponse tr = new TestRunResponse();
            tr.setId(r.getId());
            tr.setProjectId(r.getProject().getId());
            tr.setTestTitle(r.getTestCase() != null ? r.getTestCase().getTitle() : "Ad-hoc Execution");
            tr.setExecutionMode(r.getExecutionMode());
            tr.setStatus(r.getStatus());
            tr.setIsVulnerable(r.getIsVulnerable());
            tr.setOverallScore(r.getOverallScore());
            tr.setLatencyMs(r.getLatencyMs());
            return tr;
        }).collect(Collectors.toList());
        response.setRecentRuns(recentResponses);

        return response;
    }
}
