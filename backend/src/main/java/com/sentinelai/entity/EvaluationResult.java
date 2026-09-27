package com.sentinelai.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "evaluation_results", indexes = {
        @Index(name = "idx_eval_results_test_run_id", columnList = "test_run_id"),
        @Index(name = "idx_eval_results_metric_name", columnList = "metric_name")
})
public class EvaluationResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "test_run_id", nullable = false)
    private TestRun testRun;

    @NotBlank
    @Column(name = "metric_name", nullable = false, length = 50)
    private String metricName;

    @Column(nullable = false, precision = 5, scale = 4)
    private BigDecimal score;

    @Column(nullable = false, precision = 5, scale = 4)
    private BigDecimal threshold;

    @Column(nullable = false)
    private Boolean passed = true;

    @Column(columnDefinition = "TEXT")
    private String reasoning;

    @Column(name = "evaluation_model", nullable = false, length = 50)
    private String evaluationModel = "gemini-1.5-flash";

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public EvaluationResult() {}

    public EvaluationResult(TestRun testRun, String metricName, BigDecimal score, BigDecimal threshold,
                            Boolean passed, String reasoning, String evaluationModel) {
        this.testRun = testRun;
        this.metricName = metricName;
        this.score = score;
        this.threshold = threshold;
        this.passed = passed != null ? passed : true;
        this.reasoning = reasoning;
        this.evaluationModel = evaluationModel != null ? evaluationModel : "gemini-1.5-flash";
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public TestRun getTestRun() { return testRun; }
    public void setTestRun(TestRun testRun) { this.testRun = testRun; }

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
