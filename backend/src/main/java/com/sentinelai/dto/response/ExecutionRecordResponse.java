package com.sentinelai.dto.response;

import com.sentinelai.enums.NodeType;
import com.sentinelai.enums.StepStatus;

import java.time.LocalDateTime;

public class ExecutionRecordResponse {
    private Long id;
    private Long testRunId;
    private String traceId;
    private String spanId;
    private String parentSpanId;
    private String nodeName;
    private NodeType nodeType;
    private String inputState;
    private String outputState;
    private Long durationMs;
    private Integer promptTokens;
    private Integer completionTokens;
    private StepStatus status;
    private String errorDetails;
    private LocalDateTime createdAt;

    public ExecutionRecordResponse() {}

    public ExecutionRecordResponse(Long id, Long testRunId, String traceId, String spanId,
                                   String parentSpanId, String nodeName, NodeType nodeType,
                                   String inputState, String outputState, Long durationMs,
                                   Integer promptTokens, Integer completionTokens,
                                   StepStatus status, String errorDetails, LocalDateTime createdAt) {
        this.id = id;
        this.testRunId = testRunId;
        this.traceId = traceId;
        this.spanId = spanId;
        this.parentSpanId = parentSpanId;
        this.nodeName = nodeName;
        this.nodeType = nodeType;
        this.inputState = inputState;
        this.outputState = outputState;
        this.durationMs = durationMs;
        this.promptTokens = promptTokens;
        this.completionTokens = completionTokens;
        this.status = status;
        this.errorDetails = errorDetails;
        this.createdAt = createdAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getTestRunId() { return testRunId; }
    public void setTestRunId(Long testRunId) { this.testRunId = testRunId; }

    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }

    public String getSpanId() { return spanId; }
    public void setSpanId(String spanId) { this.spanId = spanId; }

    public String getParentSpanId() { return parentSpanId; }
    public void setParentSpanId(String parentSpanId) { this.parentSpanId = parentSpanId; }

    public String getNodeName() { return nodeName; }
    public void setNodeName(String nodeName) { this.nodeName = nodeName; }

    public NodeType getNodeType() { return nodeType; }
    public void setNodeType(NodeType nodeType) { this.nodeType = nodeType; }

    public String getInputState() { return inputState; }
    public void setInputState(String inputState) { this.inputState = inputState; }

    public String getOutputState() { return outputState; }
    public void setOutputState(String outputState) { this.outputState = outputState; }

    public Long getDurationMs() { return durationMs; }
    public void setDurationMs(Long durationMs) { this.durationMs = durationMs; }

    public Integer getPromptTokens() { return promptTokens; }
    public void setPromptTokens(Integer promptTokens) { this.promptTokens = promptTokens; }

    public Integer getCompletionTokens() { return completionTokens; }
    public void setCompletionTokens(Integer completionTokens) { this.completionTokens = completionTokens; }

    public StepStatus getStatus() { return status; }
    public void setStatus(StepStatus status) { this.status = status; }

    public String getErrorDetails() { return errorDetails; }
    public void setErrorDetails(String errorDetails) { this.errorDetails = errorDetails; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
