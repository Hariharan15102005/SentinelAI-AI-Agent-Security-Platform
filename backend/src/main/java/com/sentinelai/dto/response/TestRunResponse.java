package com.sentinelai.dto.response;

import com.sentinelai.enums.ExecutionMode;
import com.sentinelai.enums.RunStatus;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public class TestRunResponse {
    private Long id;
    private Long projectId;
    private Long testCaseId;
    private String testTitle;
    private ExecutionMode executionMode;
    private RunStatus status;
    private String inputPrompt;
    private String finalOutput;
    private String guardrailsApplied;
    private Boolean isVulnerable;
    private BigDecimal overallScore;
    private Long latencyMs;
    private Integer totalTokens;
    private String errorMessage;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
    private LocalDateTime createdAt;
    private List<SecurityFindingResponse> securityFindings;
    private List<EvaluationResultResponse> evaluationResults;

    public TestRunResponse() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getProjectId() { return projectId; }
    public void setProjectId(Long projectId) { this.projectId = projectId; }

    public Long getTestCaseId() { return testCaseId; }
    public void setTestCaseId(Long testCaseId) { this.testCaseId = testCaseId; }

    public String getTestTitle() { return testTitle; }
    public void setTestTitle(String testTitle) { this.testTitle = testTitle; }

    public ExecutionMode getExecutionMode() { return executionMode; }
    public void setExecutionMode(ExecutionMode executionMode) { this.executionMode = executionMode; }

    public RunStatus getStatus() { return status; }
    public void setStatus(RunStatus status) { this.status = status; }

    public String getInputPrompt() { return inputPrompt; }
    public void setInputPrompt(String inputPrompt) { this.inputPrompt = inputPrompt; }

    public String getFinalOutput() { return finalOutput; }
    public void setFinalOutput(String finalOutput) { this.finalOutput = finalOutput; }

    public String getGuardrailsApplied() { return guardrailsApplied; }
    public void setGuardrailsApplied(String guardrailsApplied) { this.guardrailsApplied = guardrailsApplied; }

    public Boolean getIsVulnerable() { return isVulnerable; }
    public void setIsVulnerable(Boolean isVulnerable) { this.isVulnerable = isVulnerable; }

    public BigDecimal getOverallScore() { return overallScore; }
    public void setOverallScore(BigDecimal overallScore) { this.overallScore = overallScore; }

    public Long getLatencyMs() { return latencyMs; }
    public void setLatencyMs(Long latencyMs) { this.latencyMs = latencyMs; }

    public Integer getTotalTokens() { return totalTokens; }
    public void setTotalTokens(Integer totalTokens) { this.totalTokens = totalTokens; }

    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }

    public LocalDateTime getStartedAt() { return startedAt; }
    public void setStartedAt(LocalDateTime startedAt) { this.startedAt = startedAt; }

    public LocalDateTime getCompletedAt() { return completedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public List<SecurityFindingResponse> getSecurityFindings() { return securityFindings; }
    public void setSecurityFindings(List<SecurityFindingResponse> securityFindings) { this.securityFindings = securityFindings; }

    public List<EvaluationResultResponse> getEvaluationResults() { return evaluationResults; }
    public void setEvaluationResults(List<EvaluationResultResponse> evaluationResults) { this.evaluationResults = evaluationResults; }
}
