package com.sentinelai.dto.request;

import com.sentinelai.enums.Severity;
import com.sentinelai.enums.TestCategory;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.List;

public class TestCaseRequest {

    @NotBlank(message = "Title is required")
    @Size(max = 150, message = "Title cannot exceed 150 characters")
    private String title;

    @NotNull(message = "Category is required")
    private TestCategory category;

    @NotBlank(message = "Input prompt is required")
    private String inputPrompt;

    private String expectedBehavior;

    private List<String> contextDocuments;

    private Severity severity = Severity.MEDIUM;

    public TestCaseRequest() {}

    public TestCaseRequest(String title, TestCategory category, String inputPrompt,
                           String expectedBehavior, List<String> contextDocuments, Severity severity) {
        this.title = title;
        this.category = category;
        this.inputPrompt = inputPrompt;
        this.expectedBehavior = expectedBehavior;
        this.contextDocuments = contextDocuments;
        this.severity = severity != null ? severity : Severity.MEDIUM;
    }

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
}
