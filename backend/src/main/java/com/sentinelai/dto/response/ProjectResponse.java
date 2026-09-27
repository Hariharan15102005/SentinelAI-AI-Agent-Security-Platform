package com.sentinelai.dto.response;

import com.sentinelai.enums.AgentType;

import java.time.LocalDateTime;

public class ProjectResponse {
    private Long id;
    private Long userId;
    private String name;
    private String description;
    private AgentType agentType;
    private String systemPrompt;
    private Long testCaseCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public ProjectResponse() {}

    public ProjectResponse(Long id, Long userId, String name, String description,
                           AgentType agentType, String systemPrompt, Long testCaseCount,
                           LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.userId = userId;
        this.name = name;
        this.description = description;
        this.agentType = agentType;
        this.systemPrompt = systemPrompt;
        this.testCaseCount = testCaseCount;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public AgentType getAgentType() { return agentType; }
    public void setAgentType(AgentType agentType) { this.agentType = agentType; }

    public String getSystemPrompt() { return systemPrompt; }
    public void setSystemPrompt(String systemPrompt) { this.systemPrompt = systemPrompt; }

    public Long getTestCaseCount() { return testCaseCount; }
    public void setTestCaseCount(Long testCaseCount) { this.testCaseCount = testCaseCount; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
