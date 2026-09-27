package com.sentinelai.dto.request;

import com.sentinelai.enums.AgentType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class ProjectRequest {

    @NotBlank(message = "Project name is required")
    @Size(max = 100, message = "Project name cannot exceed 100 characters")
    private String name;

    private String description;

    private AgentType agentType = AgentType.LANGGRAPH;

    private String systemPrompt;

    public ProjectRequest() {}

    public ProjectRequest(String name, String description, AgentType agentType, String systemPrompt) {
        this.name = name;
        this.description = description;
        this.agentType = agentType != null ? agentType : AgentType.LANGGRAPH;
        this.systemPrompt = systemPrompt;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public AgentType getAgentType() { return agentType; }
    public void setAgentType(AgentType agentType) { this.agentType = agentType; }

    public String getSystemPrompt() { return systemPrompt; }
    public void setSystemPrompt(String systemPrompt) { this.systemPrompt = systemPrompt; }
}
