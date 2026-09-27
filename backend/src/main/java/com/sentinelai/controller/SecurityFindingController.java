package com.sentinelai.controller;

import com.sentinelai.dto.response.SecurityFindingResponse;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.SecurityFindingService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/findings")
@Tag(name = "Security Findings", description = "Vulnerability findings and policy breaches explorer")
public class SecurityFindingController {

    @Autowired
    private SecurityFindingService securityFindingService;

    @GetMapping
    @Operation(summary = "List findings by project", description = "Returns all security findings recorded for a project")
    public ResponseEntity<List<SecurityFindingResponse>> getFindings(
            @RequestParam Long projectId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        List<SecurityFindingResponse> findings = securityFindingService.getFindingsByProject(projectId, currentUser.getId());
        return ResponseEntity.ok(findings);
    }

    @GetMapping("/{findingId}")
    @Operation(summary = "Get finding details", description = "Returns complete vulnerability finding details and remediation notes")
    public ResponseEntity<SecurityFindingResponse> getFindingById(
            @PathVariable Long findingId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        SecurityFindingResponse finding = securityFindingService.getFindingById(findingId, currentUser.getId());
        return ResponseEntity.ok(finding);
    }
}
