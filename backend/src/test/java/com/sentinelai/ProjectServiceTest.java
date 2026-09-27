package com.sentinelai;

import com.sentinelai.dto.request.ProjectRequest;
import com.sentinelai.dto.request.RegisterRequest;
import com.sentinelai.dto.response.ProjectResponse;
import com.sentinelai.dto.response.UserResponse;
import com.sentinelai.enums.AgentType;
import com.sentinelai.exception.UnauthorizedAccessException;
import com.sentinelai.repository.ProjectRepository;
import com.sentinelai.repository.UserRepository;
import com.sentinelai.service.ProjectService;
import com.sentinelai.service.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
public class ProjectServiceTest {

    @Autowired
    private ProjectService projectService;

    @Autowired
    private UserService userService;

    @Autowired
    private ProjectRepository projectRepository;

    @Autowired
    private UserRepository userRepository;

    private UserResponse user1;
    private UserResponse user2;

    @BeforeEach
    void setUp() {
        projectRepository.deleteAll();
        userRepository.deleteAll();

        user1 = userService.register(new RegisterRequest("alice", "alice@sentinelai.dev", "Pass123!"));
        user2 = userService.register(new RegisterRequest("bob", "bob@sentinelai.dev", "Pass123!"));
    }

    @Test
    void testCreateAndGetProject_Success() {
        // Initial state must be empty - no default or demo projects
        List<ProjectResponse> initialProjects = projectService.getProjectsForUser(user1.getId());
        assertEquals(0, initialProjects.size());

        // Create project with exact custom fields
        ProjectRequest req = new ProjectRequest("Custom Security Evaluator", "User created security agent", AgentType.CREWAI, "Custom system prompt for agent");
        ProjectResponse created = projectService.createProject(req, user1.getId());

        assertNotNull(created.getId());
        assertEquals("Custom Security Evaluator", created.getName());
        assertEquals("User created security agent", created.getDescription());
        assertEquals(AgentType.CREWAI, created.getAgentType());
        assertEquals("Custom system prompt for agent", created.getSystemPrompt());
        assertEquals(user1.getId(), created.getUserId());

        List<ProjectResponse> aliceProjects = projectService.getProjectsForUser(user1.getId());
        assertEquals(1, aliceProjects.size());
        assertEquals("Custom Security Evaluator", aliceProjects.get(0).getName());
        assertEquals("User created security agent", aliceProjects.get(0).getDescription());
        assertEquals(AgentType.CREWAI, aliceProjects.get(0).getAgentType());
        assertEquals("Custom system prompt for agent", aliceProjects.get(0).getSystemPrompt());

        List<ProjectResponse> bobProjects = projectService.getProjectsForUser(user2.getId());
        assertEquals(0, bobProjects.size());
    }

    @Test
    void testUserCannotAccessOtherUserProject() {
        ProjectRequest req = new ProjectRequest("Alice Private Agent", "Sensitive agent", AgentType.LANGGRAPH, "Secret");
        ProjectResponse created = projectService.createProject(req, user1.getId());

        // Bob attempts to get Alice's project
        assertThrows(UnauthorizedAccessException.class, () -> {
            projectService.getProjectById(created.getId(), user2.getId());
        });

        // Bob attempts to update Alice's project
        ProjectRequest updateReq = new ProjectRequest("Hacked Name", "Hacked", AgentType.LANGGRAPH, "Hacked");
        assertThrows(UnauthorizedAccessException.class, () -> {
            projectService.updateProject(created.getId(), updateReq, user2.getId());
        });

        // Bob attempts to delete Alice's project
        assertThrows(UnauthorizedAccessException.class, () -> {
            projectService.deleteProject(created.getId(), user2.getId());
        });
    }
}
