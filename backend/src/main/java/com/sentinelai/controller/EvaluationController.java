package com.sentinelai.controller;

import com.sentinelai.dto.response.EvaluationResultResponse;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.EvaluationResultService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/evaluations")
@Tag(name = "Evaluations", description = "DeepEval metrics and reliability scoring endpoints")
public class EvaluationController {

    @Autowired
    private EvaluationResultService evaluationResultService;

    @GetMapping
    @Operation(summary = "Get evaluation results", description = "Fetches DeepEval metrics for all runs under a project")
    public ResponseEntity<List<EvaluationResultResponse>> getEvaluationResults(
            @RequestParam Long projectId,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        List<EvaluationResultResponse> results = evaluationResultService.getEvaluationResultsByProject(projectId, currentUser.getId());
        return ResponseEntity.ok(results);
    }
}
