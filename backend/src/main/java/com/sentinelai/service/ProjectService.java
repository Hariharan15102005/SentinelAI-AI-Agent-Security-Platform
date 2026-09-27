package com.sentinelai.service;

import com.sentinelai.dto.request.ProjectRequest;
import com.sentinelai.dto.response.ProjectResponse;
import com.sentinelai.entity.Project;
import com.sentinelai.entity.User;
import com.sentinelai.exception.ResourceNotFoundException;
import com.sentinelai.exception.UnauthorizedAccessException;
import com.sentinelai.repository.ProjectRepository;
import com.sentinelai.repository.TestCaseRepository;
import com.sentinelai.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ProjectService {

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private TestCaseRepository testCaseRepository;

    @Autowired
    private UserRepository userRepository;

    @Transactional(readOnly = true)
    public List<ProjectResponse> getProjectsForUser(Long userId) {
        List<Project> projects = projectRepository.findByUserIdOrderByCreatedAtDesc(userId);
        return projects.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public ProjectResponse getProjectById(Long projectId, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found with id: " + projectId));

        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to access project: " + projectId);
        }

        return mapToResponse(project);
    }

    @Transactional
    public ProjectResponse createProject(ProjectRequest request, Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));

        Project project = new Project(
                user,
                request.getName(),
                request.getDescription(),
                request.getAgentType(),
                request.getSystemPrompt()
        );

        Project saved = projectRepository.save(project);
        return mapToResponse(saved);
    }

    @Transactional
    public ProjectResponse updateProject(Long projectId, ProjectRequest request, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found with id: " + projectId));

        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to update project: " + projectId);
        }

        project.setName(request.getName());
        project.setDescription(request.getDescription());
        if (request.getAgentType() != null) {
            project.setAgentType(request.getAgentType());
        }
        if (request.getSystemPrompt() != null) {
            project.setSystemPrompt(request.getSystemPrompt());
        }

        Project updated = projectRepository.save(project);
        return mapToResponse(updated);
    }

    @Transactional
    public void deleteProject(Long projectId, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new ResourceNotFoundException("Project not found with id: " + projectId));

        if (!project.getUser().getId().equals(userId)) {
            throw new UnauthorizedAccessException("You do not have permission to delete project: " + projectId);
        }

        projectRepository.delete(project);
    }

    private ProjectResponse mapToResponse(Project project) {
        long testCount = testCaseRepository.countByProjectId(project.getId());
        return new ProjectResponse(
                project.getId(),
                project.getUser().getId(),
                project.getName(),
                project.getDescription(),
                project.getAgentType(),
                project.getSystemPrompt(),
                testCount,
                project.getCreatedAt(),
                project.getUpdatedAt()
        );
    }
}
