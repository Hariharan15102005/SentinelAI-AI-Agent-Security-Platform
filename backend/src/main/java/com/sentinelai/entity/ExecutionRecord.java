package com.sentinelai.entity;

import com.sentinelai.enums.NodeType;
import com.sentinelai.enums.StepStatus;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "execution_records", indexes = {
        @Index(name = "idx_exec_records_test_run_id", columnList = "test_run_id"),
        @Index(name = "idx_exec_records_trace_span", columnList = "trace_id, span_id")
})
public class ExecutionRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "test_run_id", nullable = false)
    private TestRun testRun;

    @NotBlank
    @Column(name = "trace_id", nullable = false, length = 64)
    private String traceId;

    @NotBlank
    @Column(name = "span_id", nullable = false, length = 64)
    private String spanId;

    @Column(name = "parent_span_id", length = 64)
    private String parentSpanId;

    @NotBlank
    @Column(name = "node_name", nullable = false, length = 100)
    private String nodeName;

    @Enumerated(EnumType.STRING)
    @Column(name = "node_type", nullable = false, length = 30)
    private NodeType nodeType;

    @Column(name = "input_state", columnDefinition = "TEXT")
    private String inputState; // JSON snapshot

    @Column(name = "output_state", columnDefinition = "TEXT")
    private String outputState; // JSON snapshot

    @Column(name = "duration_ms", nullable = false)
    private Long durationMs;

    @Column(name = "prompt_tokens", nullable = false)
    private Integer promptTokens = 0;

    @Column(name = "completion_tokens", nullable = false)
    private Integer completionTokens = 0;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private StepStatus status = StepStatus.SUCCESS;

    @Column(name = "error_details", columnDefinition = "TEXT")
    private String errorDetails;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public ExecutionRecord() {}

    public ExecutionRecord(TestRun testRun, String traceId, String spanId, String parentSpanId,
                           String nodeName, NodeType nodeType, String inputState, String outputState,
                           Long durationMs, Integer promptTokens, Integer completionTokens,
                           StepStatus status, String errorDetails) {
        this.testRun = testRun;
        this.traceId = traceId;
        this.spanId = spanId;
        this.parentSpanId = parentSpanId;
        this.nodeName = nodeName;
        this.nodeType = nodeType;
        this.inputState = inputState;
        this.outputState = outputState;
        this.durationMs = durationMs;
        this.promptTokens = promptTokens != null ? promptTokens : 0;
        this.completionTokens = completionTokens != null ? completionTokens : 0;
        this.status = status != null ? status : StepStatus.SUCCESS;
        this.errorDetails = errorDetails;
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public TestRun getTestRun() { return testRun; }
    public void setTestRun(TestRun testRun) { this.testRun = testRun; }

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
