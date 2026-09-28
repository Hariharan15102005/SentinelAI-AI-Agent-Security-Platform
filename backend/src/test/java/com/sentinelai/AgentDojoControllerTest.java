package com.sentinelai;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sentinelai.dto.request.AgentDojoRunRequest;
import com.sentinelai.dto.request.RegisterRequest;
import com.sentinelai.dto.response.UserResponse;
import com.sentinelai.repository.*;
import com.sentinelai.security.JwtTokenProvider;
import com.sentinelai.security.UserPrincipal;
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
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
public class AgentDojoControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserService userService;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ObjectMapper objectMapper;

    private String jwtToken;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();

        UserResponse user = userService.register(new RegisterRequest("dojotester", "dojo@sentinelai.dev", "SecOpsPass123!"));
        UserPrincipal principal = new UserPrincipal(user.getId(), user.getUsername(), user.getEmail(), "hashed",
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER")));
        jwtToken = jwtTokenProvider.generateToken(new UsernamePasswordAuthenticationToken(principal, null, principal.getAuthorities()));
    }

    @Test
    void testGetSuites_Success() throws Exception {
        mockMvc.perform(get("/api/v1/agentdojo/suites")
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$[0].id").isNotEmpty())
                .andExpect(jsonPath("$[0].tools").isArray());
    }

    @Test
    void testGetScenarios_Success() throws Exception {
        mockMvc.perform(get("/api/v1/agentdojo/scenarios")
                        .param("suite", "workspace")
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$[0].suite").value("workspace"))
                .andExpect(jsonPath("$[0].category").value("SECURITY_AGENTDOJO_INDIRECT_INJECTION"));
    }

    @Test
    void testExecuteRun_Success() throws Exception {
        AgentDojoRunRequest req = new AgentDojoRunRequest(
                "workspace_email_exfiltration_01",
                "SECURED",
                List.of("PromptInjectionDetector", "PIIAnonymizer"),
                "gemini-1.5-flash"
        );

        mockMvc.perform(post("/api/v1/agentdojo/run")
                        .header("Authorization", "Bearer " + jwtToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.scenarioId").value("workspace_email_exfiltration_01"))
                .andExpect(jsonPath("$.benchmarkVerdict").exists())
                .andExpect(jsonPath("$.sentinelaiVerdict").exists())
                .andExpect(jsonPath("$.status").value("COMPLETED"));
    }

    @Test
    void testUnauthenticated_Returns403() throws Exception {
        mockMvc.perform(get("/api/v1/agentdojo/suites"))
                .andExpect(status().isForbidden());
    }
}
