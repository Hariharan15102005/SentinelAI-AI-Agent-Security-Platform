package com.sentinelai.dto.response;

public class SentinelAIVerdictResponse {
    private Boolean guardrailsActive;
    private Boolean blocked;
    private Boolean threatDetected;
    private Integer findingsCount;
    private Double containmentRate;

    public SentinelAIVerdictResponse() {
    }

    public SentinelAIVerdictResponse(Boolean guardrailsActive, Boolean blocked, Boolean threatDetected,
                                     Integer findingsCount, Double containmentRate) {
        this.guardrailsActive = guardrailsActive;
        this.blocked = blocked;
        this.threatDetected = threatDetected;
        this.findingsCount = findingsCount;
        this.containmentRate = containmentRate;
    }

    public Boolean getGuardrailsActive() {
        return guardrailsActive;
    }

    public void setGuardrailsActive(Boolean guardrailsActive) {
        this.guardrailsActive = guardrailsActive;
    }

    public Boolean getBlocked() {
        return blocked;
    }

    public void setBlocked(Boolean blocked) {
        this.blocked = blocked;
    }

    public Boolean getThreatDetected() {
        return threatDetected;
    }

    public void setThreatDetected(Boolean threatDetected) {
        this.threatDetected = threatDetected;
    }

    public Integer getFindingsCount() {
        return findingsCount;
    }

    public void setFindingsCount(Integer findingsCount) {
        this.findingsCount = findingsCount;
    }

    public Double getContainmentRate() {
        return containmentRate;
    }

    public void setContainmentRate(Double containmentRate) {
        this.containmentRate = containmentRate;
    }
}
