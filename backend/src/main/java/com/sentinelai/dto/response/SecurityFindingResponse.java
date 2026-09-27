package com.sentinelai.dto.response;

import com.sentinelai.enums.FindingAction;
import com.sentinelai.enums.Severity;
import com.sentinelai.enums.ThreatType;

import java.time.LocalDateTime;

public class SecurityFindingResponse {
    private Long id;
    private Long testRunId;
    private Long projectId;
    private String title;
    private ThreatType threatType;
    private Severity severity;
    private String guardrailRule;
    private String flaggedContent;
    private FindingAction actionTaken;
    private String remediationNotes;
    private LocalDateTime createdAt;

    public SecurityFindingResponse() {}

    public SecurityFindingResponse(Long id, Long testRunId, Long projectId, String title,
                                   ThreatType threatType, Severity severity, String guardrailRule,
                                   String flaggedContent, FindingAction actionTaken,
                                   String remediationNotes, LocalDateTime createdAt) {
        this.id = id;
        this.testRunId = testRunId;
        this.projectId = projectId;
        this.title = title;
        this.threatType = threatType;
        this.severity = severity;
        this.guardrailRule = guardrailRule;
        this.flaggedContent = flaggedContent;
        this.actionTaken = actionTaken;
        this.remediationNotes = remediationNotes;
        this.createdAt = createdAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getTestRunId() { return testRunId; }
    public void setTestRunId(Long testRunId) { this.testRunId = testRunId; }

    public Long getProjectId() { return projectId; }
    public void setProjectId(Long projectId) { this.projectId = projectId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public ThreatType getThreatType() { return threatType; }
    public void setThreatType(ThreatType threatType) { this.threatType = threatType; }

    public Severity getSeverity() { return severity; }
    public void setSeverity(Severity severity) { this.severity = severity; }

    public String getGuardrailRule() { return guardrailRule; }
    public void setGuardrailRule(String guardrailRule) { this.guardrailRule = guardrailRule; }

    public String getFlaggedContent() { return flaggedContent; }
    public void setFlaggedContent(String flaggedContent) { this.flaggedContent = flaggedContent; }

    public FindingAction getActionTaken() { return actionTaken; }
    public void setActionTaken(FindingAction actionTaken) { this.actionTaken = actionTaken; }

    public String getRemediationNotes() { return remediationNotes; }
    public void setRemediationNotes(String remediationNotes) { this.remediationNotes = remediationNotes; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
