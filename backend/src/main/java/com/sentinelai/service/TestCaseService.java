package com.sentinelai.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sentinelai.dto.request.TestCaseRequest;
import com.sentinelai.dto.response.TestCaseResponse;
import com.sentinelai.entity.Project;
import com.sentinelai.entity.TestCase;
import com.sentinelai.enums.TestCategory;
import com.sentinelai.exception.ResourceNotFoundException;
import com.sentinelai.exception.UnauthorizedAccessException;
import com.sentinelai.repository.ProjectRepository;
import com.sentinelai.repository.TestCaseRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class TestCaseService {

    @Autowired
    private TestCaseRepository testCaseRepository;

    @Autowired
    private ProjectRepository projectRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Transactional(readOnly = true)
    public List<TestCaseResponse> getTestCases(Long projectId, TestCategory category, Long userId) {
        verifyProjectOwnership(projectId, userId);

        List<TestCase> testCases;
        if (category != null) {
            testCases = testCaseRepository.findByProjectIdAndCategory(projectId, category);
        } else {
            testCases = testCaseRepository.findByProjectIdOrderByCreatedAtDesc(projectId);
        }

        return testCases.stream().map(this::mapToResponse).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public TestCaseResponse getTestCaseById(Long projectId, Long testCaseId, Long userId) {
        verifyProjectOwnership(projectId, userId);

        TestCase testCase = testCaseRepository.findByIdAndProjectId(testCaseId, projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Test case not found with id: " + testCaseId));

        return mapToResponse(testCase);
    }

    @Transactional
    public TestCaseResponse createTestCase(Long projectId, TestCaseRequest request, Long userId) {
        Project project = verifyProjectOwnership(projectId, userId);

        String contextDocsJson = null;
        try {
            if (request.getContextDocuments() != null) {
                contextDocsJson = objectMapper.writeValueAsString(request.getContextDocuments());
            }
        } catch (Exception e) {
            contextDocsJson = "[]";
        }

        TestCase testCase = new TestCase(
                project,
                request.getTitle(),
                request.getCategory(),
                request.getInputPrompt(),
                request.getExpectedBehavior(),
                contextDocsJson,
                request.getSeverity()
        );

        TestCase saved = testCaseRepository.save(testCase);
        return mapToResponse(saved);
    }

    @Transactional
    public TestCaseResponse updateTestCase(Long projectId, Long testCaseId, TestCaseRequest request, Long userId) {
        verifyProjectOwnership(projectId, userId);

        TestCase testCase = testCaseRepository.findByIdAndProjectId(testCaseId, projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Test case not found with id: " + testCaseId));

        testCase.setTitle(request.getTitle());
        testCase.setCategory(request.getCategory());
        testCase.setInputPrompt(request.getInputPrompt());
        testCase.setExpectedBehavior(request.getExpectedBehavior());
        testCase.setSeverity(request.getSeverity());

        try {
            if (request.getContextDocuments() != null) {
                testCase.setContextDocuments(objectMapper.writeValueAsString(request.getContextDocuments()));
            }
        } catch (Exception e) {
            // retain existing
        }

        TestCase updated = testCaseRepository.save(testCase);
        return mapToResponse(updated);
    }

    @Transactional
    public void deleteTestCase(Long projectId, Long testCaseId, Long userId) {
        verifyProjectOwnership(projectId, userId);

        TestCase testCase = testCaseRepository.findByIdAndProjectId(testCaseId, projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Test case not found with id: " + testCaseId));

        testCaseRepository.delete(testCase);
    }

    private Project verifyProjectOwnership(Long projectId, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found with id: " + projectId));

        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to access project: " + projectId);
        }
        return project;
    }

    private TestCaseResponse mapToResponse(TestCase testCase) {
        List<String> contextDocs = Collections.emptyList();
        try {
            if (testCase.getContextDocuments() != null && !testCase.getContextDocuments().isBlank()) {
                contextDocs = objectMapper.readValue(testCase.getContextDocuments(), new TypeReference<List<String>>() {});
            }
        } catch (Exception e) {
            contextDocs = Collections.emptyList();
        }

        return new TestCaseResponse(
                testCase.getId(),
                testCase.getProject().getId(),
                testCase.getTitle(),
                testCase.getCategory(),
                testCase.getInputPrompt(),
                testCase.getExpectedBehavior(),
                contextDocs,
                testCase.getSeverity(),
                testCase.getCreatedAt(),
                testCase.getUpdatedAt()
        );
    }
}
