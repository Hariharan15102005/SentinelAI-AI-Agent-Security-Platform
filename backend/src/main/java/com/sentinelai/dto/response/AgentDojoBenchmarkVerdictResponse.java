package com.sentinelai.dto.response;

public class AgentDojoBenchmarkVerdictResponse {
    private Boolean userTaskCompleted;
    private Boolean attackSuccessful;
    private String agentdojoNativeDefense;
    private String attackObjective;

    public AgentDojoBenchmarkVerdictResponse() {
    }

    public AgentDojoBenchmarkVerdictResponse(Boolean userTaskCompleted, Boolean attackSuccessful,
                                             String agentdojoNativeDefense, String attackObjective) {
        this.userTaskCompleted = userTaskCompleted;
        this.attackSuccessful = attackSuccessful;
        this.agentdojoNativeDefense = agentdojoNativeDefense;
        this.attackObjective = attackObjective;
    }

    public Boolean getUserTaskCompleted() {
        return userTaskCompleted;
    }

    public void setUserTaskCompleted(Boolean userTaskCompleted) {
        this.userTaskCompleted = userTaskCompleted;
    }

    public Boolean getAttackSuccessful() {
        return attackSuccessful;
    }

    public void setAttackSuccessful(Boolean attackSuccessful) {
        this.attackSuccessful = attackSuccessful;
    }

    public String getAgentdojoNativeDefense() {
        return agentdojoNativeDefense;
    }

    public void setAgentdojoNativeDefense(String agentdojoNativeDefense) {
        this.agentdojoNativeDefense = agentdojoNativeDefense;
    }

    public String getAttackObjective() {
        return attackObjective;
    }

    public void setAttackObjective(String attackObjective) {
        this.attackObjective = attackObjective;
    }
}
