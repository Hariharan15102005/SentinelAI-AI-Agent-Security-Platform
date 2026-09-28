package com.sentinelai.controller;

import com.sentinelai.dto.request.AgentDojoRunRequest;
import com.sentinelai.dto.response.AgentDojoRunResponse;
import com.sentinelai.dto.response.AgentDojoScenarioResponse;
import com.sentinelai.dto.response.AgentDojoSuiteResponse;
import com.sentinelai.service.AgentDojoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/agentdojo")
@Tag(name = "AgentDojo Benchmark", description = "Endpoints for discovering suites, scenarios, and executing benchmark runs")
public class AgentDojoController {

    @Autowired
    private AgentDojoService agentDojoService;

    @GetMapping("/suites")
    @Operation(summary = "List AgentDojo suites", description = "Retrieves all available benchmark suites metadata")
    public ResponseEntity<List<AgentDojoSuiteResponse>> getSuites() {
        List<AgentDojoSuiteResponse> suites = agentDojoService.getSuites();
        return ResponseEntity.ok(suites);
    }

    @GetMapping("/scenarios")
    @Operation(summary = "List AgentDojo scenarios", description = "Retrieves scenario catalog filtered optionally by suite")
    public ResponseEntity<List<AgentDojoScenarioResponse>> getScenarios(@RequestParam(required = false) String suite) {
        List<AgentDojoScenarioResponse> scenarios = agentDojoService.getScenarios(suite);
        return ResponseEntity.ok(scenarios);
    }

    @PostMapping("/run")
    @Operation(summary = "Execute AgentDojo benchmark scenario", description = "Executes an adversarial indirect injection scenario against the agent")
    public ResponseEntity<AgentDojoRunResponse> executeBenchmark(@Valid @RequestBody AgentDojoRunRequest request) {
        AgentDojoRunResponse response = agentDojoService.executeRun(request);
        return ResponseEntity.ok(response);
    }
}
