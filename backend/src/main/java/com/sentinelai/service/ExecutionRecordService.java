package com.sentinelai.service;

import com.sentinelai.dto.response.ExecutionRecordResponse;
import com.sentinelai.entity.ExecutionRecord;
import com.sentinelai.entity.Project;
import com.sentinelai.entity.TestRun;
import com.sentinelai.exception.ResourceNotFoundException;
import com.sentinelai.exception.UnauthorizedAccessException;
import com.sentinelai.repository.ExecutionRecordRepository;
import com.sentinelai.repository.ProjectRepository;
import com.sentinelai.repository.TestRunRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ExecutionRecordService {

    @Autowired
    private ExecutionRecordRepository executionRecordRepository;

    @Autowired
    private TestRunRepository testRunRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Transactional(readOnly = true)
    public List<ExecutionRecordResponse> getTraceWaterfall(Long runId, Long userId) {
        TestRun run = testRunRepository.findById(runId)
                .orElseThrow(() -> new ResourceNotFoundException("Test run not found with id: " + runId));

        Project project = run.getProject();
        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to access traces for project: " + project.getId());
        }

        return executionRecordRepository.findByTestRunIdOrderByCreatedAtAsc(runId).stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private ExecutionRecordResponse mapToResponse(ExecutionRecord r) {
        return new ExecutionRecordResponse(
                r.getId(),
                r.getTestRun().getId(),
                r.getTraceId(),
                r.getSpanId(),
                r.getParentSpanId(),
                r.getNodeName(),
                r.getNodeType(),
                r.getInputState(),
                r.getOutputState(),
                r.getDurationMs(),
                r.getPromptTokens(),
                r.getCompletionTokens(),
                r.getStatus(),
                r.getErrorDetails(),
                r.getCreatedAt()
        );
    }
}
