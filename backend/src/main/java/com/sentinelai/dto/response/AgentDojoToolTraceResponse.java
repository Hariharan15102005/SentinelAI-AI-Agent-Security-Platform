package com.sentinelai.dto.response;

import java.util.Map;

public class AgentDojoToolTraceResponse {
    private String toolName;
    private Map<String, Object> arguments;
    private String rawOutput;
    private Integer latencyMs;
    private String guardrailStatus;

    public AgentDojoToolTraceResponse() {
    }

    public AgentDojoToolTraceResponse(String toolName, Map<String, Object> arguments, String rawOutput,
                                      Integer latencyMs, String guardrailStatus) {
        this.toolName = toolName;
        this.arguments = arguments;
        this.rawOutput = rawOutput;
        this.latencyMs = latencyMs;
        this.guardrailStatus = guardrailStatus;
    }

    public String getToolName() {
        return toolName;
    }

    public void setToolName(String toolName) {
        this.toolName = toolName;
    }

    public Map<String, Object> getArguments() {
        return arguments;
    }

    public void setArguments(Map<String, Object> arguments) {
        this.arguments = arguments;
    }

    public String getRawOutput() {
        return rawOutput;
    }

    public void setRawOutput(String rawOutput) {
        this.rawOutput = rawOutput;
    }

    public Integer getLatencyMs() {
        return latencyMs;
    }

    public void setLatencyMs(Integer latencyMs) {
        this.latencyMs = latencyMs;
    }

    public String getGuardrailStatus() {
        return guardrailStatus;
    }

    public void setGuardrailStatus(String guardrailStatus) {
        this.guardrailStatus = guardrailStatus;
    }
}
