package com.sentinelai.dto.response;

public class AgentDojoScenarioResponse {
    private String id;
    private String suite;
    private String name;
    private String category;
    private String userTaskId;
    private String userTaskPrompt;
    private String injectionTaskId;
    private String injectionTaskGoal;
    private String attackType;
    private String attackPayload;
    private String severity;

    public AgentDojoScenarioResponse() {
    }

    public AgentDojoScenarioResponse(String id, String suite, String name, String category,
                                     String userTaskId, String userTaskPrompt, String injectionTaskId,
                                     String injectionTaskGoal, String attackType, String attackPayload,
                                     String severity) {
        this.id = id;
        this.suite = suite;
        this.name = name;
        this.category = category;
        this.userTaskId = userTaskId;
        this.userTaskPrompt = userTaskPrompt;
        this.injectionTaskId = injectionTaskId;
        this.injectionTaskGoal = injectionTaskGoal;
        this.attackType = attackType;
        this.attackPayload = attackPayload;
        this.severity = severity;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getSuite() {
        return suite;
    }

    public void setSuite(String suite) {
        this.suite = suite;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getUserTaskId() {
        return userTaskId;
    }

    public void setUserTaskId(String userTaskId) {
        this.userTaskId = userTaskId;
    }

    public String getUserTaskPrompt() {
        return userTaskPrompt;
    }

    public void setUserTaskPrompt(String userTaskPrompt) {
        this.userTaskPrompt = userTaskPrompt;
    }

    public String getInjectionTaskId() {
        return injectionTaskId;
    }

    public void setInjectionTaskId(String injectionTaskId) {
        this.injectionTaskId = injectionTaskId;
    }

    public String getInjectionTaskGoal() {
        return injectionTaskGoal;
    }

    public void setInjectionTaskGoal(String injectionTaskGoal) {
        this.injectionTaskGoal = injectionTaskGoal;
    }

    public String getAttackType() {
        return attackType;
    }

    public void setAttackType(String attackType) {
        this.attackType = attackType;
    }

    public String getAttackPayload() {
        return attackPayload;
    }

    public void setAttackPayload(String attackPayload) {
        this.attackPayload = attackPayload;
    }

    public String getSeverity() {
        return severity;
    }

    public void setSeverity(String severity) {
        this.severity = severity;
    }
}
