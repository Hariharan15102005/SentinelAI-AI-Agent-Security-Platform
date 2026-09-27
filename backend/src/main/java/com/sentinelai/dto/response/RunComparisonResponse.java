package com.sentinelai.dto.response;

import java.math.BigDecimal;
import java.util.Map;

public class RunComparisonResponse {
    private TestCaseSummary testCase;
    private RunComparisonDetail baseline;
    private RunComparisonDetail secured;
    private ComparisonDelta delta;

    public RunComparisonResponse() {}

    public static class TestCaseSummary {
        private Long id;
        private String title;
        private String inputPrompt;

        public TestCaseSummary() {}
        public TestCaseSummary(Long id, String title, String inputPrompt) {
            this.id = id;
            this.title = title;
            this.inputPrompt = inputPrompt;
        }

        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getInputPrompt() { return inputPrompt; }
        public void setInputPrompt(String inputPrompt) { this.inputPrompt = inputPrompt; }
    }

    public static class RunComparisonDetail {
        private Long runId;
        private Boolean isVulnerable;
        private Long latencyMs;
        private Integer totalTokens;
        private String finalOutput;
        private BigDecimal overallScore;
        private Integer findingsCount;
        private BigDecimal faithfulnessScore;

        public RunComparisonDetail() {}

        public Long getRunId() { return runId; }
        public void setRunId(Long runId) { this.runId = runId; }
        public Boolean getIsVulnerable() { return isVulnerable; }
        public void setIsVulnerable(Boolean isVulnerable) { this.isVulnerable = isVulnerable; }
        public Long getLatencyMs() { return latencyMs; }
        public void setLatencyMs(Long latencyMs) { this.latencyMs = latencyMs; }
        public Integer getTotalTokens() { return totalTokens; }
        public void setTotalTokens(Integer totalTokens) { this.totalTokens = totalTokens; }
        public String getFinalOutput() { return finalOutput; }
        public void setFinalOutput(String finalOutput) { this.finalOutput = finalOutput; }
        public BigDecimal getOverallScore() { return overallScore; }
        public void setOverallScore(BigDecimal overallScore) { this.overallScore = overallScore; }
        public Integer getFindingsCount() { return findingsCount; }
        public void setFindingsCount(Integer findingsCount) { this.findingsCount = findingsCount; }
        public BigDecimal getFaithfulnessScore() { return faithfulnessScore; }
        public void setFaithfulnessScore(BigDecimal faithfulnessScore) { this.faithfulnessScore = faithfulnessScore; }
    }

    public static class ComparisonDelta {
        private Boolean vulnerabilityMitigated;
        private Long latencyOverheadMs;
        private Integer tokenSavings;

        public ComparisonDelta() {}
        public ComparisonDelta(Boolean vulnerabilityMitigated, Long latencyOverheadMs, Integer tokenSavings) {
            this.vulnerabilityMitigated = vulnerabilityMitigated;
            this.latencyOverheadMs = latencyOverheadMs;
            this.tokenSavings = tokenSavings;
        }

        public Boolean getVulnerabilityMitigated() { return vulnerabilityMitigated; }
        public void setVulnerabilityMitigated(Boolean vulnerabilityMitigated) { this.vulnerabilityMitigated = vulnerabilityMitigated; }
        public Long getLatencyOverheadMs() { return latencyOverheadMs; }
        public void setLatencyOverheadMs(Long latencyOverheadMs) { this.latencyOverheadMs = latencyOverheadMs; }
        public Integer getTokenSavings() { return tokenSavings; }
        public void setTokenSavings(Integer tokenSavings) { this.tokenSavings = tokenSavings; }
    }

    public TestCaseSummary getTestCase() { return testCase; }
    public void setTestCase(TestCaseSummary testCase) { this.testCase = testCase; }

    public RunComparisonDetail getBaseline() { return baseline; }
    public void setBaseline(RunComparisonDetail baseline) { this.baseline = baseline; }

    public RunComparisonDetail getSecured() { return secured; }
    public void setSecured(RunComparisonDetail secured) { this.secured = secured; }

    public ComparisonDelta getDelta() { return delta; }
    public void setDelta(ComparisonDelta delta) { this.delta = delta; }
}
