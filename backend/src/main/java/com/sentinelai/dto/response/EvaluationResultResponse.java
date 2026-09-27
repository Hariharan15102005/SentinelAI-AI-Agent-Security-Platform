package com.sentinelai.dto.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class EvaluationResultResponse {
    private Long id;
    private Long testRunId;
    private String metricName;
    private BigDecimal score;
    private BigDecimal threshold;
    private Boolean passed;
    private String reasoning;
    private String evaluationModel;
    private LocalDateTime createdAt;

    public EvaluationResultResponse() {}

    public EvaluationResultResponse(Long id, Long testRunId, String metricName, BigDecimal score,
                                    BigDecimal threshold, Boolean passed, String reasoning,
                                    String evaluationModel, LocalDateTime createdAt) {
        this.id = id;
        this.testRunId = testRunId;
        this.metricName = metricName;
        this.score = score;
        this.threshold = threshold;
        this.passed = passed;
        this.reasoning = reasoning;
        this.evaluationModel = evaluationModel;
        this.createdAt = createdAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getTestRunId() { return testRunId; }
    public void setTestRunId(Long testRunId) { this.testRunId = testRunId; }

    public String getMetricName() { return metricName; }
    public void setMetricName(String metricName) { this.metricName = metricName; }

    public BigDecimal getScore() { return score; }
    public void setScore(BigDecimal score) { this.score = score; }

    public BigDecimal getThreshold() { return threshold; }
    public void setThreshold(BigDecimal threshold) { this.threshold = threshold; }

    public Boolean getPassed() { return passed; }
    public void setPassed(Boolean passed) { this.passed = passed; }

    public String getReasoning() { return reasoning; }
    public void setReasoning(String reasoning) { this.reasoning = reasoning; }

    public String getEvaluationModel() { return evaluationModel; }
    public void setEvaluationModel(String evaluationModel) { this.evaluationModel = evaluationModel; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
