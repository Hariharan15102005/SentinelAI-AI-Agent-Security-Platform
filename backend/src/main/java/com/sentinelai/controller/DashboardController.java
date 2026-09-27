package com.sentinelai.controller;

import com.sentinelai.dto.response.DashboardSummaryResponse;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.DashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/dashboard")
@Tag(name = "Dashboard", description = "Aggregated security and reliability metrics")
public class DashboardController {

    @Autowired
    private DashboardService dashboardService;

    @GetMapping("/summary")
    @Operation(summary = "Get dashboard summary", description = "Returns aggregated KPIs, pass rates, and threat distributions for a project")
    public ResponseEntity<DashboardSummaryResponse> getDashboardSummary(
            @RequestParam Long projectId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        DashboardSummaryResponse summary = dashboardService.getDashboardSummary(projectId, currentUser.getId());
        return ResponseEntity.ok(summary);
    }
}
