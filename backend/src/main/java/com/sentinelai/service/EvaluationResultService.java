package com.sentinelai.service;

import com.sentinelai.dto.response.EvaluationResultResponse;
import com.sentinelai.entity.EvaluationResult;
import com.sentinelai.entity.Project;
import com.sentinelai.exception.ResourceNotFoundException;
import com.sentinelai.exception.UnauthorizedAccessException;
import com.sentinelai.repository.EvaluationResultRepository;
import com.sentinelai.repository.ProjectRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class EvaluationResultService {

    @Autowired
    private EvaluationResultRepository evaluationResultRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Transactional(readOnly = true)
    public List<EvaluationResultResponse> getEvaluationResultsByProject(Long projectId, Long userId) {
        verifyProjectOwnership(projectId, userId);
        return evaluationResultRepository.findByProjectId(projectId).stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private void verifyProjectOwnership(Long projectId, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found with id: " + projectId));

        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to access project: " + projectId);
        }
    }

    private EvaluationResultResponse mapToResponse(EvaluationResult e) {
        return new EvaluationResultResponse(
                e.getId(),
                e.getTestRun().getId(),
                e.getMetricName(),
                e.getScore(),
                e.getThreshold(),
                e.getPassed(),
                e.getReasoning(),
                e.getEvaluationModel(),
                e.getCreatedAt()
        );
    }
}
