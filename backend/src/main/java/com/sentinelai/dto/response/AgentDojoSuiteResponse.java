package com.sentinelai.dto.response;

import java.util.List;

public class AgentDojoSuiteResponse {
    private String id;
    private String name;
    private String description;
    private List<String> tools;
    private String environment;
    private Integer userTaskCount;
    private Integer injectionTaskCount;
    private String version;

    public AgentDojoSuiteResponse() {
    }

    public AgentDojoSuiteResponse(String id, String name, String description, List<String> tools,
                                  String environment, Integer userTaskCount, Integer injectionTaskCount, String version) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.tools = tools;
        this.environment = environment;
        this.userTaskCount = userTaskCount;
        this.injectionTaskCount = injectionTaskCount;
        this.version = version;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public List<String> getTools() {
        return tools;
    }

    public void setTools(List<String> tools) {
        this.tools = tools;
    }

    public String getEnvironment() {
        return environment;
    }

    public void setEnvironment(String environment) {
        this.environment = environment;
    }

    public Integer getUserTaskCount() {
        return userTaskCount;
    }

    public void setUserTaskCount(Integer userTaskCount) {
        this.userTaskCount = userTaskCount;
    }

    public Integer getInjectionTaskCount() {
        return injectionTaskCount;
    }

    public void setInjectionTaskCount(Integer injectionTaskCount) {
        this.injectionTaskCount = injectionTaskCount;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }
}
