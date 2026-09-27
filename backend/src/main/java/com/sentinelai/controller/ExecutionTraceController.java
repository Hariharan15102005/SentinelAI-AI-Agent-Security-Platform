package com.sentinelai.controller;

import com.sentinelai.dto.response.ExecutionRecordResponse;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.ExecutionRecordService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/traces")
@Tag(name = "Execution Traces", description = "OpenTelemetry trace spans and waterfall explorer")
public class ExecutionTraceController {

    @Autowired
    private ExecutionRecordService executionRecordService;

    @GetMapping("/{runId}")
    @Operation(summary = "Get execution waterfall", description = "Returns hierarchical OpenTelemetry trace spans for a test run")
    public ResponseEntity<List<ExecutionRecordResponse>> getTraceWaterfall(
            @PathVariable Long runId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        List<ExecutionRecordResponse> traces = executionRecordService.getTraceWaterfall(runId, currentUser.getId());
        return ResponseEntity.ok(traces);
    }
}
