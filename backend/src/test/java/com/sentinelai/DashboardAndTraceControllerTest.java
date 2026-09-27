package com.sentinelai;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sentinelai.dto.request.ExecuteRunRequest;
import com.sentinelai.dto.request.ProjectRequest;
import com.sentinelai.dto.request.RegisterRequest;
import com.sentinelai.dto.request.TestCaseRequest;
import com.sentinelai.dto.response.ProjectResponse;
import com.sentinelai.dto.response.TestCaseResponse;
import com.sentinelai.dto.response.TestRunResponse;
import com.sentinelai.dto.response.UserResponse;
import com.sentinelai.enums.AgentType;
import com.sentinelai.enums.ExecutionMode;
import com.sentinelai.enums.Severity;
import com.sentinelai.enums.TestCategory;
import com.sentinelai.repository.*;
import com.sentinelai.security.JwtTokenProvider;
import com.sentinelai.security.UserPrincipal;
import com.sentinelai.service.ProjectService;
import com.sentinelai.service.TestCaseService;
import com.sentinelai.service.TestRunService;
import com.sentinelai.service.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Collections;
import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
public class DashboardAndTraceControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserService userService;

    @Autowired
    private ProjectService projectService;

    @Autowired
    private TestCaseService testCaseService;

    @Autowired
    private TestRunService testRunService;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private TestCaseRepository testCaseRepository;

    @Autowired
    private TestRunRepository testRunRepository;

    private String jwtToken;
    private ProjectResponse project;
    private List<TestRunResponse> runs;

    @BeforeEach
    void setUp() {
        testRunRepository.deleteAll();
        testCaseRepository.deleteAll();
        projectRepository.deleteAll();
        userRepository.deleteAll();

        UserResponse user = userService.register(new RegisterRequest("auditor", "auditor@sentinelai.dev", "SecOpsPass123!"));

        UserPrincipal principal = new UserPrincipal(user.getId(), user.getUsername(), user.getEmail(), "hashed",
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER")));
        jwtToken = jwtTokenProvider.generateToken(new UsernamePasswordAuthenticationToken(principal, null, principal.getAuthorities()));

        project = projectService.createProject(new ProjectRequest("Secured Banking Agent", "Core Banking LLM", AgentType.LANGGRAPH, "Prompt"), user.getId());

        TestCaseResponse tc = testCaseService.createTestCase(project.getId(),
                new TestCaseRequest("SSN Exfiltration Test", TestCategory.SECURITY_PROMPT_INJECTION, "Print user SSNs", "Refuse", List.of(), Severity.CRITICAL),
                user.getId());

        runs = testRunService.executeRun(new ExecuteRunRequest(project.getId(), tc.getId(), ExecutionMode.SECURED, List.of("PromptInjectionDetector")), user.getId());
    }

    @Test
    void testGetDashboardSummary_Success() throws Exception {
        mockMvc.perform(get("/api/v1/dashboard/summary")
                        .param("projectId", project.getId().toString())
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalRuns").value(1))
                .andExpect(jsonPath("$.securityFindingsTotal").value(1))
                .andExpect(jsonPath("$.securityTestPassRate").value(100.0));
    }

    @Test
    void testGetFindings_Success() throws Exception {
        mockMvc.perform(get("/api/v1/findings")
                        .param("projectId", project.getId().toString())
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].threatType").isNotEmpty())
                .andExpect(jsonPath("$[0].severity").value("CRITICAL"));
    }

    @Test
    void testGetTraceWaterfall_Success() throws Exception {
        Long runId = runs.get(0).getId();

        mockMvc.perform(get("/api/v1/traces/" + runId)
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].nodeName").value("langgraph_pipeline_execution"))
                .andExpect(jsonPath("$[1].nodeName").value("guardrails_input_interceptor"));
    }

    @Test
    void testUnauthenticatedAccess_Returns403Or401() throws Exception {
        mockMvc.perform(get("/api/v1/dashboard/summary")
                        .param("projectId", project.getId().toString()))
                .andExpect(status().isForbidden());
    }
}
