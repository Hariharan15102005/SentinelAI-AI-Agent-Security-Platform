package com.sentinelai.controller;

import com.sentinelai.dto.request.TestCaseRequest;
import com.sentinelai.dto.response.TestCaseResponse;
import com.sentinelai.enums.TestCategory;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.TestCaseService;
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
@RequestMapping("/api/v1/projects/{projectId}/test-cases")
@Tag(name = "Test Cases", description = "Test scenario CRUD endpoints")
public class TestCaseController {

    @Autowired
    private TestCaseService testCaseService;

    @GetMapping
    @Operation(summary = "List test cases for project", description = "Returns all test cases for a project with optional category filter")
    public ResponseEntity<List<TestCaseResponse>> getTestCases(
            @PathVariable Long projectId,
            @RequestParam(required = false) TestCategory category,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        List<TestCaseResponse> testCases = testCaseService.getTestCases(projectId, category, currentUser.getId());
        return ResponseEntity.ok(testCases);
    }

    @GetMapping("/{testCaseId}")
    @Operation(summary = "Get test case by ID", description = "Returns details for a specific test case")
    public ResponseEntity<TestCaseResponse> getTestCaseById(
            @PathVariable Long projectId,
            @PathVariable Long testCaseId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        TestCaseResponse testCase = testCaseService.getTestCaseById(projectId, testCaseId, currentUser.getId());
        return ResponseEntity.ok(testCase);
    }

    @PostMapping
    @Operation(summary = "Create test case", description = "Adds a new test case to the specified project")
    public ResponseEntity<TestCaseResponse> createTestCase(
            @PathVariable Long projectId,
            @Valid @RequestBody TestCaseRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        TestCaseResponse created = testCaseService.createTestCase(projectId, request, currentUser.getId());
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    @PutMapping("/{testCaseId}")
    @Operation(summary = "Update test case", description = "Modifies an existing test case")
    public ResponseEntity<TestCaseResponse> updateTestCase(
            @PathVariable Long projectId,
            @PathVariable Long testCaseId,
            @Valid @RequestBody TestCaseRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        TestCaseResponse updated = testCaseService.updateTestCase(projectId, testCaseId, request, currentUser.getId());
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{testCaseId}")
    @Operation(summary = "Delete test case", description = "Removes a test case from the project")
    public ResponseEntity<Void> deleteTestCase(
            @PathVariable Long projectId,
            @PathVariable Long testCaseId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        testCaseService.deleteTestCase(projectId, testCaseId, currentUser.getId());
        return ResponseEntity.noContent().build();
    }
}
