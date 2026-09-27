package com.sentinelai.entity;

import com.sentinelai.enums.FindingAction;
import com.sentinelai.enums.Severity;
import com.sentinelai.enums.ThreatType;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "security_findings", indexes = {
        @Index(name = "idx_findings_test_run_id", columnList = "test_run_id"),
        @Index(name = "idx_findings_severity_threat", columnList = "severity, threat_type")
})
public class SecurityFinding {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "test_run_id", nullable = false)
    private TestRun testRun;

    @Enumerated(EnumType.STRING)
    @Column(name = "threat_type", nullable = false, length = 50)
    private ThreatType threatType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Severity severity;

    @NotBlank
    @Column(name = "guardrail_rule", nullable = false, length = 100)
    private String guardrailRule;

    @Column(name = "flagged_content", nullable = false, columnDefinition = "TEXT")
    private String flaggedContent;

    @Enumerated(EnumType.STRING)
    @Column(name = "action_taken", nullable = false, length = 30)
    private FindingAction actionTaken = FindingAction.BLOCKED;

    @Column(name = "remediation_notes", columnDefinition = "TEXT")
    private String remediationNotes;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public SecurityFinding() {}

    public SecurityFinding(TestRun testRun, ThreatType threatType, Severity severity,
                           String guardrailRule, String flaggedContent, FindingAction actionTaken, String remediationNotes) {
        this.testRun = testRun;
        this.threatType = threatType;
        this.severity = severity;
        this.guardrailRule = guardrailRule;
        this.flaggedContent = flaggedContent;
        this.actionTaken = actionTaken != null ? actionTaken : FindingAction.BLOCKED;
        this.remediationNotes = remediationNotes;
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public TestRun getTestRun() { return testRun; }
    public void setTestRun(TestRun testRun) { this.testRun = testRun; }

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
