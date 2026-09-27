package com.sentinelai.dto.request;

import com.sentinelai.enums.ExecutionMode;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public class ExecuteRunRequest {

    @NotNull(message = "Project ID is required")
    private Long projectId;

    private Long testCaseId;

    private List<Long> testCaseIds;

    @NotNull(message = "Execution mode is required (BASELINE or SECURED)")
    private ExecutionMode executionMode = ExecutionMode.SECURED;

    private List<String> guardrails;

    private String customPrompt;

    public ExecuteRunRequest() {}

    public ExecuteRunRequest(Long projectId, Long testCaseId, ExecutionMode executionMode, List<String> guardrails) {
        this.projectId = projectId;
        this.testCaseId = testCaseId;
        this.executionMode = executionMode != null ? executionMode : ExecutionMode.SECURED;
        this.guardrails = guardrails;
    }

    public Long getProjectId() { return projectId; }
    public void setProjectId(Long projectId) { this.projectId = projectId; }

    public Long getTestCaseId() { return testCaseId; }
    public void setTestCaseId(Long testCaseId) { this.testCaseId = testCaseId; }

    public List<Long> getTestCaseIds() { return testCaseIds; }
    public void setTestCaseIds(List<Long> testCaseIds) { this.testCaseIds = testCaseIds; }

    public ExecutionMode getExecutionMode() { return executionMode; }
    public void setExecutionMode(ExecutionMode executionMode) { this.executionMode = executionMode; }

    public List<String> getGuardrails() { return guardrails; }
    public void setGuardrails(List<String> guardrails) { this.guardrails = guardrails; }

    public String getCustomPrompt() { return customPrompt; }
    public void setCustomPrompt(String customPrompt) { this.customPrompt = customPrompt; }
}
