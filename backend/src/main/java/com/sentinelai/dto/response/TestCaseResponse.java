package com.sentinelai.dto.response;

import com.sentinelai.enums.Severity;
import com.sentinelai.enums.TestCategory;

import java.time.LocalDateTime;
import java.util.List;

public class TestCaseResponse {
    private Long id;
    private Long projectId;
    private String title;
    private TestCategory category;
    private String inputPrompt;
    private String expectedBehavior;
    private List<String> contextDocuments;
    private Severity severity;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public TestCaseResponse() {}

    public TestCaseResponse(Long id, Long projectId, String title, TestCategory category,
                            String inputPrompt, String expectedBehavior, List<String> contextDocuments,
                            Severity severity, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.projectId = projectId;
        this.title = title;
        this.category = category;
        this.inputPrompt = inputPrompt;
        this.expectedBehavior = expectedBehavior;
        this.contextDocuments = contextDocuments;
        this.severity = severity;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getProjectId() { return projectId; }
    public void setProjectId(Long projectId) { this.projectId = projectId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public TestCategory getCategory() { return category; }
    public void setCategory(TestCategory category) { this.category = category; }

    public String getInputPrompt() { return inputPrompt; }
    public void setInputPrompt(String inputPrompt) { this.inputPrompt = inputPrompt; }

    public String getExpectedBehavior() { return expectedBehavior; }
    public void setExpectedBehavior(String expectedBehavior) { this.expectedBehavior = expectedBehavior; }

    public List<String> getContextDocuments() { return contextDocuments; }
    public void setContextDocuments(List<String> contextDocuments) { this.contextDocuments = contextDocuments; }

    public Severity getSeverity() { return severity; }
    public void setSeverity(Severity severity) { this.severity = severity; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
