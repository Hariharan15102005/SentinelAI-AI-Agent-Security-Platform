package com.sentinelai.entity;

import com.sentinelai.enums.Severity;
import com.sentinelai.enums.TestCategory;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "test_cases", indexes = {
        @Index(name = "idx_test_cases_project_id", columnList = "project_id"),
        @Index(name = "idx_test_cases_category", columnList = "category")
})
public class TestCase {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @NotBlank
    @Size(max = 150)
    @Column(nullable = false, length = 150)
    private String title;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private TestCategory category;

    @NotBlank
    @Column(name = "input_prompt", nullable = false, columnDefinition = "TEXT")
    private String inputPrompt;

    @Column(name = "expected_behavior", columnDefinition = "TEXT")
    private String expectedBehavior;

    @Column(name = "context_documents", columnDefinition = "TEXT")
    private String contextDocuments; // Stored as JSON or comma-delimited text

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Severity severity = Severity.MEDIUM;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "testCase", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<TestRun> testRuns = new ArrayList<>();

    public TestCase() {}

    public TestCase(Project project, String title, TestCategory category, String inputPrompt,
                    String expectedBehavior, String contextDocuments, Severity severity) {
        this.project = project;
        this.title = title;
        this.category = category;
        this.inputPrompt = inputPrompt;
        this.expectedBehavior = expectedBehavior;
        this.contextDocuments = contextDocuments;
        this.severity = severity != null ? severity : Severity.MEDIUM;
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Project getProject() { return project; }
    public void setProject(Project project) { this.project = project; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public TestCategory getCategory() { return category; }
    public void setCategory(TestCategory category) { this.category = category; }

    public String getInputPrompt() { return inputPrompt; }
    public void setInputPrompt(String inputPrompt) { this.inputPrompt = inputPrompt; }

    public String getExpectedBehavior() { return expectedBehavior; }
    public void setExpectedBehavior(String expectedBehavior) { this.expectedBehavior = expectedBehavior; }

    public String getContextDocuments() { return contextDocuments; }
    public void setContextDocuments(String contextDocuments) { this.contextDocuments = contextDocuments; }

    public Severity getSeverity() { return severity; }
    public void setSeverity(Severity severity) { this.severity = severity; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public List<TestRun> getTestRuns() { return testRuns; }
    public void setTestRuns(List<TestRun> testRuns) { this.testRuns = testRuns; }
}
