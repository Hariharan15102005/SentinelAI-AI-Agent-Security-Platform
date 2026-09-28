package com.sentinelai.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class AIServiceClient {

    private static final Logger logger = LoggerFactory.getLogger(AIServiceClient.class);

    private final RestClient restClient;
    private final String internalToken;

    public AIServiceClient(
            @Value("${sentinelai.ai-service.base-url:http://localhost:8000/api/v1}") String baseUrl,
            @Value("${sentinelai.ai-service.internal-token:sentinelai_internal_token_secret_key_2026}") String internalToken,
            @Value("${sentinelai.ai-service.timeout-seconds:60}") int timeoutSeconds) {
        this.internalToken = internalToken;
        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .defaultHeader("X-Internal-Token", internalToken)
                .build();
    }

    /**
     * Dispatches an execution payload to the FastAPI LangGraph sandbox with W3C Trace Context propagation
     */
    public Map<String, Object> executeAgentRun(Map<String, Object> payload) {
        try {
            String traceId = UUID.randomUUID().toString().replace("-", "");
            String spanId = UUID.randomUUID().toString().replace("-", "").substring(0, 16);
            String traceparent = String.format("00-%s-%s-01", traceId, spanId);

            logger.info("Dispatching agent execution to AI microservice: runId={}, traceId={}", payload.get("runId"), traceId);
            return restClient.post()
                    .uri("/agent/run")
                    .header("traceparent", traceparent)
                    .header("X-Trace-Id", traceId)
                    .body(payload)
                    .retrieve()
                    .body(Map.class);
        } catch (Exception ex) {
            logger.warn("AI Microservice communication not reachable (expected before Phase 4): {}", ex.getMessage());
            return null;
        }
    }

    /**
     * Fetches metadata for all available AgentDojo suites.
     */
    public List<Map<String, Object>> getAgentDojoSuites() {
        try {
            logger.info("Fetching AgentDojo suites from AI microservice");
            return restClient.get()
                    .uri("/agentdojo/suites")
                    .retrieve()
                    .body(new ParameterizedTypeReference<List<Map<String, Object>>>() {});
        } catch (Exception ex) {
            logger.warn("Could not retrieve AgentDojo suites from AI microservice: {}", ex.getMessage());
            return List.of();
        }
    }

    /**
     * Fetches scenarios for a given suite (or all suites if null).
     */
    public List<Map<String, Object>> getAgentDojoScenarios(String suite) {
        try {
            String uri = (suite != null && !suite.isBlank())
                    ? "/agentdojo/scenarios?suite=" + suite
                    : "/agentdojo/scenarios";
            logger.info("Fetching AgentDojo scenarios from AI microservice with uri: {}", uri);
            return restClient.get()
                    .uri(uri)
                    .retrieve()
                    .body(new ParameterizedTypeReference<List<Map<String, Object>>>() {});
        } catch (Exception ex) {
            logger.warn("Could not retrieve AgentDojo scenarios from AI microservice: {}", ex.getMessage());
            return List.of();
        }
    }

    /**
     * Executes an AgentDojo scenario benchmark run against the AI microservice.
     */
    public Map<String, Object> executeAgentDojoRun(Map<String, Object> payload) {
        try {
            String traceId = UUID.randomUUID().toString().replace("-", "");
            String spanId = UUID.randomUUID().toString().replace("-", "").substring(0, 16);
            String traceparent = String.format("00-%s-%s-01", traceId, spanId);

            logger.info("Dispatching AgentDojo benchmark execution to AI microservice: scenarioId={}, traceId={}",
                    payload.get("scenarioId"), traceId);
            return restClient.post()
                    .uri("/agentdojo/run")
                    .header("traceparent", traceparent)
                    .header("X-Trace-Id", traceId)
                    .body(payload)
                    .retrieve()
                    .body(Map.class);
        } catch (Exception ex) {
            logger.warn("Could not execute AgentDojo benchmark on AI microservice: {}", ex.getMessage());
            return null;
        }
    }
}
