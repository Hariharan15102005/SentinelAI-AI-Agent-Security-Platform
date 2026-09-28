package com.sentinelai.dto.request;

import jakarta.validation.constraints.NotBlank;
import java.util.List;

public class AgentDojoRunRequest {

    @NotBlank(message = "Scenario ID is required")
    private String scenarioId;

    private String executionMode = "SECURED";

    private List<String> guardrails;

    private String modelName = "gemini-1.5-flash";

    public AgentDojoRunRequest() {
    }

    public AgentDojoRunRequest(String scenarioId, String executionMode, List<String> guardrails, String modelName) {
        this.scenarioId = scenarioId;
        this.executionMode = executionMode;
        this.guardrails = guardrails;
        this.modelName = modelName;
    }

    public String getScenarioId() {
        return scenarioId;
    }

    public void setScenarioId(String scenarioId) {
        this.scenarioId = scenarioId;
    }

    public String getExecutionMode() {
        return executionMode;
    }

    public void setExecutionMode(String executionMode) {
        this.executionMode = executionMode;
    }

    public List<String> getGuardrails() {
        return guardrails;
    }

    public void setGuardrails(List<String> guardrails) {
        this.guardrails = guardrails;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }
}
