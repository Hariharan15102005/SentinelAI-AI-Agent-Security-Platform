package com.sentinelai.service;

import com.sentinelai.dto.response.SecurityFindingResponse;
import com.sentinelai.entity.Project;
import com.sentinelai.entity.SecurityFinding;
import com.sentinelai.exception.ResourceNotFoundException;
import com.sentinelai.exception.UnauthorizedAccessException;
import com.sentinelai.repository.ProjectRepository;
import com.sentinelai.repository.SecurityFindingRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class SecurityFindingService {

    @Autowired
    private SecurityFindingRepository securityFindingRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Transactional(readOnly = true)
    public List<SecurityFindingResponse> getFindingsByProject(Long projectId, Long userId) {
        verifyProjectOwnership(projectId, userId);
        return securityFindingRepository.findByProjectId(projectId).stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public SecurityFindingResponse getFindingById(Long findingId, Long userId) {
        SecurityFinding finding = securityFindingRepository.findById(findingId)
                .orElseThrow(() -> new ResourceNotFoundException("Security finding not found with id: " + findingId));

        verifyProjectOwnership(finding.getTestRun().getProject().getId(), userId);
        return mapToResponse(finding);
    }

    private void verifyProjectOwnership(Long projectId, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found with id: " + projectId));

        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to access project: " + projectId);
        }
    }

    private SecurityFindingResponse mapToResponse(SecurityFinding f) {
        return new SecurityFindingResponse(
                f.getId(),
                f.getTestRun().getId(),
                f.getTestRun().getProject().getId(),
                "Finding: " + f.getThreatType().name() + " via " + f.getGuardrailRule(),
                f.getThreatType(),
                f.getSeverity(),
                f.getGuardrailRule(),
                f.getFlaggedContent(),
                f.getActionTaken(),
                f.getRemediationNotes(),
                f.getCreatedAt()
        );
    }
}
