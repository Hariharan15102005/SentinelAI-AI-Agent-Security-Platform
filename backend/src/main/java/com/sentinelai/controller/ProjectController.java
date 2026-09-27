package com.sentinelai.controller;

import com.sentinelai.dto.request.ProjectRequest;
import com.sentinelai.dto.response.ProjectResponse;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.ProjectService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/projects")
@Tag(name = "Projects", description = "AI agent projects management endpoints")
public class ProjectController {

    @Autowired
    private ProjectService projectService;

    @GetMapping
    @Operation(summary = "List user projects", description = "Returns all agent projects owned by the authenticated user")
    public ResponseEntity<List<ProjectResponse>> getProjects(@AuthenticationPrincipal UserPrincipal currentUser) {
        List<ProjectResponse> projects = projectService.getProjectsForUser(currentUser.getId());
        return ResponseEntity.ok(projects);
    }

    @GetMapping("/{projectId}")
    @Operation(summary = "Get project by ID", description = "Returns project details if owned by user")
    public ResponseEntity<ProjectResponse> getProjectById(
            @PathVariable Long projectId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        ProjectResponse response = projectService.getProjectById(projectId, currentUser.getId());
        return ResponseEntity.ok(response);
    }

    @PostMapping
    @Operation(summary = "Create project", description = "Creates a new agent project under user's workspace")
    public ResponseEntity<ProjectResponse> createProject(
            @Valid @RequestBody ProjectRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        ProjectResponse response = projectService.createProject(request, currentUser.getId());
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    @PutMapping("/{projectId}")
    @Operation(summary = "Update project", description = "Updates an existing agent project")
    public ResponseEntity<ProjectResponse> updateProject(
            @PathVariable Long projectId,
            @Valid @RequestBody ProjectRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        ProjectResponse response = projectService.updateProject(projectId, request, currentUser.getId());
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{projectId}")
    @Operation(summary = "Delete project", description = "Deletes an agent project and its test cases")
    public ResponseEntity<Void> deleteProject(
            @PathVariable Long projectId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        projectService.deleteProject(projectId, currentUser.getId());
        return ResponseEntity.noContent().build();
    }
}
