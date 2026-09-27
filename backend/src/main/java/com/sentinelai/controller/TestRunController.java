package com.sentinelai.controller;

import com.sentinelai.dto.request.ExecuteRunRequest;
import com.sentinelai.dto.response.RunComparisonResponse;
import com.sentinelai.dto.response.TestRunResponse;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.TestRunService;
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
@RequestMapping("/api/v1/runs")
@Tag(name = "Test Runs", description = "AI test execution and comparison endpoints")
public class TestRunController {

    @Autowired
    private TestRunService testRunService;

    @GetMapping
    @Operation(summary = "List test runs", description = "Retrieves all execution runs for a given project")
    public ResponseEntity<List<TestRunResponse>> getRuns(
            @RequestParam Long projectId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        List<TestRunResponse> runs = testRunService.getRunsByProject(projectId, currentUser.getId());
        return ResponseEntity.ok(runs);
    }

    @GetMapping("/{runId}")
    @Operation(summary = "Get run details", description = "Fetches complete run execution details, findings, and evaluation scores")
    public ResponseEntity<TestRunResponse> getRunById(
            @PathVariable Long runId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        TestRunResponse run = testRunService.getRunById(runId, currentUser.getId());
        return ResponseEntity.ok(run);
    }

    @PostMapping("/execute")
    @Operation(summary = "Execute test run", description = "Triggers an agent test run in BASELINE or SECURED mode")
    public ResponseEntity<List<TestRunResponse>> executeRun(
            @Valid @RequestBody ExecuteRunRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        List<TestRunResponse> responses = testRunService.executeRun(request, currentUser.getId());
        return new ResponseEntity<>(responses, HttpStatus.ACCEPTED);
    }

    @GetMapping("/compare")
    @Operation(summary = "Compare runs", description = "Performs side-by-side delta comparison between a baseline and secured run")
    public ResponseEntity<RunComparisonResponse> compareRuns(
            @RequestParam Long baselineRunId,
            @RequestParam Long securedRunId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        RunComparisonResponse comparison = testRunService.compareRuns(baselineRunId, securedRunId, currentUser.getId());
        return ResponseEntity.ok(comparison);
    }
}
