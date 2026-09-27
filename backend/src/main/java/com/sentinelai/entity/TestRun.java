package com.sentinelai.entity;

import com.sentinelai.enums.ExecutionMode;
import com.sentinelai.enums.RunStatus;
import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "test_runs", indexes = {
        @Index(name = "idx_test_runs_project_created", columnList = "project_id, created_at"),
        @Index(name = "idx_test_runs_mode_status", columnList = "execution_mode, status")
})
public class TestRun {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "test_case_id")
    private TestCase testCase;

    @Enumerated(EnumType.STRING)
    @Column(name = "execution_mode", nullable = false, length = 20)
    private ExecutionMode executionMode = ExecutionMode.SECURED;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private RunStatus status = RunStatus.QUEUED;

    @Column(name = "input_prompt", nullable = false, columnDefinition = "TEXT")
    private String inputPrompt;

    @Column(name = "final_output", columnDefinition = "TEXT")
    private String finalOutput;

    @Column(name = "guardrails_applied", columnDefinition = "TEXT")
    private String guardrailsApplied; // JSON or comma-separated list of active rules

    @Column(name = "is_vulnerable", nullable = false)
    private Boolean isVulnerable = false;

    @Column(name = "overall_score", precision = 5, scale = 2)
    private BigDecimal overallScore;

    @Column(name = "latency_ms")
    private Long latencyMs;

    @Column(name = "total_tokens")
    private Integer totalTokens;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "testRun", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<SecurityFinding> securityFindings = new ArrayList<>();

    @OneToMany(mappedBy = "testRun", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<EvaluationResult> evaluationResults = new ArrayList<>();

    @OneToMany(mappedBy = "testRun", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<ExecutionRecord> executionRecords = new ArrayList<>();

    public TestRun() {}

    public TestRun(Project project, TestCase testCase, ExecutionMode executionMode, String inputPrompt) {
        this.project = project;
        this.testCase = testCase;
        this.executionMode = executionMode != null ? executionMode : ExecutionMode.SECURED;
        this.inputPrompt = inputPrompt;
        this.status = RunStatus.QUEUED;
        this.startedAt = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Project getProject() { return project; }
    public void setProject(Project project) { this.project = project; }

    public TestCase getTestCase() { return testCase; }
    public void setTestCase(TestCase testCase) { this.testCase = testCase; }

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

    public List<SecurityFinding> getSecurityFindings() { return securityFindings; }
    public void setSecurityFindings(List<SecurityFinding> securityFindings) { this.securityFindings = securityFindings; }

    public List<EvaluationResult> getEvaluationResults() { return evaluationResults; }
    public void setEvaluationResults(List<EvaluationResult> evaluationResults) { this.evaluationResults = evaluationResults; }

    public List<ExecutionRecord> getExecutionRecords() { return executionRecords; }
    public void setExecutionRecords(List<ExecutionRecord> executionRecords) { this.executionRecords = executionRecords; }
}
