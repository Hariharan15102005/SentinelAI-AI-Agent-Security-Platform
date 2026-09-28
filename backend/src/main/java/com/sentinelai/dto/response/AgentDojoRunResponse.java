package com.sentinelai.dto.response;

import java.util.List;

public class AgentDojoRunResponse {
    private String runId;
    private String scenarioId;
    private String scenarioName;
    private String suite;
    private String category;
    private String userTaskPrompt;
    private String injectionTaskGoal;
    private String attackType;
    private String executionMode;
    private List<String> guardrailsApplied;
    private String modelName;
    private String traceId;
    private Integer latencyMs;
    private String status;
    private String finalOutput;
    private Boolean isVulnerable;
    private AgentDojoBenchmarkVerdictResponse benchmarkVerdict;
    private SentinelAIVerdictResponse sentinelaiVerdict;
    private List<SecurityFindingResponse> securityFindings;
    private List<AgentDojoToolTraceResponse> toolTraces;

    public AgentDojoRunResponse() {
    }

    public String getRunId() {
        return runId;
    }

    public void setRunId(String runId) {
        this.runId = runId;
    }

    public String getScenarioId() {
        return scenarioId;
    }

    public void setScenarioId(String scenarioId) {
        this.scenarioId = scenarioId;
    }

    public String getScenarioName() {
        return scenarioName;
    }

    public void setScenarioName(String scenarioName) {
        this.scenarioName = scenarioName;
    }

    public String getSuite() {
        return suite;
    }

    public void setSuite(String suite) {
        this.suite = suite;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getUserTaskPrompt() {
        return userTaskPrompt;
    }

    public void setUserTaskPrompt(String userTaskPrompt) {
        this.userTaskPrompt = userTaskPrompt;
    }

    public String getInjectionTaskGoal() {
        return injectionTaskGoal;
    }

    public void setInjectionTaskGoal(String injectionTaskGoal) {
        this.injectionTaskGoal = injectionTaskGoal;
    }

    public String getAttackType() {
        return attackType;
    }

    public void setAttackType(String attackType) {
        this.attackType = attackType;
    }

    public String getExecutionMode() {
        return executionMode;
    }

    public void setExecutionMode(String executionMode) {
        this.executionMode = executionMode;
    }

    public List<String> getGuardrailsApplied() {
        return guardrailsApplied;
    }

    public void setGuardrailsApplied(List<String> guardrailsApplied) {
        this.guardrailsApplied = guardrailsApplied;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public String getTraceId() {
        return traceId;
    }

    public void setTraceId(String traceId) {
        this.traceId = traceId;
    }

    public Integer getLatencyMs() {
        return latencyMs;
    }

    public void setLatencyMs(Integer latencyMs) {
        this.latencyMs = latencyMs;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getFinalOutput() {
        return finalOutput;
    }

    public void setFinalOutput(String finalOutput) {
        this.finalOutput = finalOutput;
    }

    public Boolean getIsVulnerable() {
        return isVulnerable;
    }

    public void setIsVulnerable(Boolean vulnerable) {
        isVulnerable = vulnerable;
    }

    public AgentDojoBenchmarkVerdictResponse getBenchmarkVerdict() {
        return benchmarkVerdict;
    }

    public void setBenchmarkVerdict(AgentDojoBenchmarkVerdictResponse benchmarkVerdict) {
        this.benchmarkVerdict = benchmarkVerdict;
    }

    public SentinelAIVerdictResponse getSentinelaiVerdict() {
        return sentinelaiVerdict;
    }

    public void setSentinelaiVerdict(SentinelAIVerdictResponse sentinelaiVerdict) {
        this.sentinelaiVerdict = sentinelaiVerdict;
    }

    public List<SecurityFindingResponse> getSecurityFindings() {
        return securityFindings;
    }

    public void setSecurityFindings(List<SecurityFindingResponse> securityFindings) {
        this.securityFindings = securityFindings;
    }

    public List<AgentDojoToolTraceResponse> getToolTraces() {
        return toolTraces;
    }

    public void setToolTraces(List<AgentDojoToolTraceResponse> toolTraces) {
        this.toolTraces = toolTraces;
    }
}
