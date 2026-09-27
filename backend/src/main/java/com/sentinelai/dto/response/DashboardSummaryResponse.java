package com.sentinelai.dto.response;

import java.util.List;
import java.util.Map;

public class DashboardSummaryResponse {
    private Long totalRuns;
    private Long securityFindingsTotal;
    private Double vulnerabilityRate;
    private Double guardrailMitigationRate;
    private Double averageLatencyMs;
    private Double averageFaithfulnessScore;
    private Double securityTestPassRate;
    private Double taskSuccessRate;
    private List<ThreatDistributionItem> threatDistribution;
    private List<SeverityDistributionItem> findingsBySeverity;
    private List<TestRunResponse> recentRuns;

    public DashboardSummaryResponse() {}

    public static class ThreatDistributionItem {
        private String type;
        private Long count;

        public ThreatDistributionItem() {}
        public ThreatDistributionItem(String type, Long count) {
            this.type = type;
            this.count = count;
        }

        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        public Long getCount() { return count; }
        public void setCount(Long count) { this.count = count; }
    }

    public static class SeverityDistributionItem {
        private String name;
        private Long count;
        private String color;

        public SeverityDistributionItem() {}
        public SeverityDistributionItem(String name, Long count, String color) {
            this.name = name;
            this.count = count;
            this.color = color;
        }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public Long getCount() { return count; }
        public void setCount(Long count) { this.count = count; }
        public String getColor() { return color; }
        public void setColor(String color) { this.color = color; }
    }

    public Long getTotalRuns() { return totalRuns; }
    public void setTotalRuns(Long totalRuns) { this.totalRuns = totalRuns; }

    public Long getSecurityFindingsTotal() { return securityFindingsTotal; }
    public void setSecurityFindingsTotal(Long securityFindingsTotal) { this.securityFindingsTotal = securityFindingsTotal; }

    public Double getVulnerabilityRate() { return vulnerabilityRate; }
    public void setVulnerabilityRate(Double vulnerabilityRate) { this.vulnerabilityRate = vulnerabilityRate; }

    public Double getGuardrailMitigationRate() { return guardrailMitigationRate; }
    public void setGuardrailMitigationRate(Double guardrailMitigationRate) { this.guardrailMitigationRate = guardrailMitigationRate; }

    public Double getAverageLatencyMs() { return averageLatencyMs; }
    public void setAverageLatencyMs(Double averageLatencyMs) { this.averageLatencyMs = averageLatencyMs; }

    public Double getAverageFaithfulnessScore() { return averageFaithfulnessScore; }
    public void setAverageFaithfulnessScore(Double averageFaithfulnessScore) { this.averageFaithfulnessScore = averageFaithfulnessScore; }

    public Double getSecurityTestPassRate() { return securityTestPassRate; }
    public void setSecurityTestPassRate(Double securityTestPassRate) { this.securityTestPassRate = securityTestPassRate; }

    public Double getTaskSuccessRate() { return taskSuccessRate; }
    public void setTaskSuccessRate(Double taskSuccessRate) { this.taskSuccessRate = taskSuccessRate; }

    public List<ThreatDistributionItem> getThreatDistribution() { return threatDistribution; }
    public void setThreatDistribution(List<ThreatDistributionItem> threatDistribution) { this.threatDistribution = threatDistribution; }

    public List<SeverityDistributionItem> getFindingsBySeverity() { return findingsBySeverity; }
    public void setFindingsBySeverity(List<SeverityDistributionItem> findingsBySeverity) { this.findingsBySeverity = findingsBySeverity; }

    public List<TestRunResponse> getRecentRuns() { return recentRuns; }
    public void setRecentRuns(List<TestRunResponse> recentRuns) { this.recentRuns = recentRuns; }
}
