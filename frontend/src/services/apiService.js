// ==============================================================================
// SentinelAI Frontend API Service
// Connects directly to Spring Boot Backend REST APIs with real data handling
// ==============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

class ApiService {
  constructor() {
    this.tokenKey = 'sentinelai_jwt_token';
    this.userKey = 'sentinelai_current_user';
  }

  // --- Auth Token Helpers ---
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  }

  clearAuth() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  getCurrentUser() {
    try {
      const u = localStorage.getItem(this.userKey);
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  }

  async ensureAuthenticated() {
    if (this.getToken()) return this.getToken();
    try {
      // Try login first with default dev user
      const loginRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'Password123!' })
      });
      if (loginRes.ok) {
        const data = await loginRes.json();
        const jwt = data.token || data.accessToken;
        if (jwt) {
          this.setToken(jwt);
          localStorage.setItem(this.userKey, JSON.stringify(data.user || { id: 1, username: 'admin' }));
          return jwt;
        }
      } else {
        // Register default dev user if not found
        const regRes = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: 'admin',
            email: 'admin@sentinelai.dev',
            password: 'Password123!',
            role: 'ROLE_ADMIN'
          })
        });
        if (regRes.ok) {
          // Then login
          const retryLogin = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'admin', password: 'Password123!' })
          });
          if (retryLogin.ok) {
            const data = await retryLogin.json();
            const jwt = data.token || data.accessToken;
            if (jwt) {
              this.setToken(jwt);
              localStorage.setItem(this.userKey, JSON.stringify(data.user || { id: 1, username: 'admin' }));
              return jwt;
            }
          }
        }
      }
    } catch (e) {
      console.warn('Session auto-init failed:', e.message);
    }
    return null;
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    if (!this.getToken() && !endpoint.startsWith('/auth/')) {
      await this.ensureAuthenticated();
    }

    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      if (response.status === 401) {
        console.warn('Unauthorized request to', endpoint);
      }
      if (!response.ok) {
        let errMessage = `HTTP Error ${response.status}: ${response.statusText}`;
        try {
          const errBody = await response.json();
          if (errBody && errBody.message) {
            errMessage = errBody.message;
          }
        } catch {
          const text = await response.text().catch(() => '');
          if (text) errMessage = text;
        }
        throw new Error(errMessage);
      }
      // Return null for 204 No Content
      if (response.status === 204) return null;
      return await response.json();
    } catch (error) {
      console.warn(`API error for ${endpoint}: ${error.message}`);
      throw error;
    }
  }

  // --- Authentication ---
  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    const jwt = data.token || data.accessToken;
    if (data && jwt) {
      this.setToken(jwt);
      localStorage.setItem(this.userKey, JSON.stringify(data.user));
    }
    return data;
  }

  async register(username, email, password) {
    return await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, role: 'ROLE_USER' })
    });
  }

  // --- Projects ---
  async getProjects() {
    try {
      const data = await this.request('/projects');
      return Array.isArray(data) ? data : [];
    } catch (e) {
      console.error('Failed to load projects from backend', e);
      return [];
    }
  }

  async getProjectById(id) {
    try {
      return await this.request(`/projects/${id}`);
    } catch (e) {
      console.error(`Failed to fetch project ${id}`, e);
      return null;
    }
  }

  async createProject(projectData) {
    return await this.request('/projects', {
      method: 'POST',
      body: JSON.stringify(projectData)
    });
  }

  async updateProject(id, projectData) {
    return await this.request(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(projectData)
    });
  }

  async deleteProject(id) {
    return await this.request(`/projects/${id}`, {
      method: 'DELETE'
    });
  }

  // --- Test Cases ---
  async getTestCases(projectId) {
    if (!projectId) return [];
    try {
      const data = await this.request(`/projects/${projectId}/test-cases`);
      return Array.isArray(data) ? data : [];
    } catch (e) {
      console.error(`Failed to load test cases for project ${projectId}`, e);
      return [];
    }
  }

  async createTestCase(testCaseData) {
    const { projectId, ...payload } = testCaseData;
    if (!projectId) {
      throw new Error('Project ID is required to create a test scenario');
    }
    return await this.request(`/projects/${projectId}/test-cases`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async deleteTestCase(id, projectId) {
    if (!projectId) {
      return await this.request(`/test-cases/${id}`, { method: 'DELETE' });
    }
    return await this.request(`/projects/${projectId}/test-cases/${id}`, {
      method: 'DELETE'
    });
  }

  // --- Test Execution ---
  async getRuns(projectId) {
    if (!projectId) return [];
    try {
      const data = await this.request(`/runs?projectId=${projectId}`);
      return Array.isArray(data) ? data : [];
    } catch (e) {
      console.error(`Failed to load runs for project ${projectId}`, e);
      return [];
    }
  }

  async getRunById(runId) {
    if (!runId) return null;
    try {
      return await this.request(`/runs/${runId}`);
    } catch (e) {
      console.error(`Failed to load run ${runId}`, e);
      return null;
    }
  }

  async executeRun({ projectId, testCaseIds, testCaseId, executionMode = 'SECURED', guardrails = [], customPrompt }) {
    const body = {
      projectId: Number(projectId),
      testCaseIds: testCaseIds || (testCaseId ? [testCaseId] : []),
      testCaseId: testCaseId || (testCaseIds && testCaseIds.length > 0 ? testCaseIds[0] : null),
      executionMode,
      guardrails,
      customPrompt
    };
    return await this.request('/runs/execute', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }

  // --- Run Comparison ---
  async compareRuns(baselineRunId, securedRunId) {
    if (!baselineRunId || !securedRunId) return null;
    try {
      return await this.request(`/runs/compare?baselineRunId=${baselineRunId}&securedRunId=${securedRunId}`);
    } catch (e) {
      console.error('Failed to compare runs', e);
      return null;
    }
  }

  // --- Security Findings ---
  async getSecurityFindings(projectId) {
    if (!projectId) return [];
    try {
      const data = await this.request(`/findings?projectId=${projectId}`);
      return Array.isArray(data) ? data : [];
    } catch (e) {
      console.error(`Failed to load security findings for project ${projectId}`, e);
      return [];
    }
  }

  async getFindingById(id) {
    if (!id) return null;
    try {
      return await this.request(`/findings/${id}`);
    } catch (e) {
      console.error(`Failed to load finding ${id}`, e);
      return null;
    }
  }

  // --- Evaluation & DeepEval Metrics ---
  async getEvaluationMetrics(projectId) {
    if (!projectId) return { projectId: Number(projectId), metrics: [], historyTrends: [] };
    try {
      const data = await this.request(`/evaluations?projectId=${projectId}`);
      if (Array.isArray(data) && data.length > 0) {
        const metricsMap = {};
        for (const item of data) {
          const mName = item.metricName || 'FAITHFULNESS';
          if (!metricsMap[mName]) {
            metricsMap[mName] = {
              scores: [],
              threshold: item.threshold != null ? item.threshold : 0.85,
              model: item.evaluationModel || 'gemini-1.5-flash'
            };
          }
          metricsMap[mName].scores.push(item.score);
        }

        const formattedMetrics = Object.keys(metricsMap).map((k, idx) => {
          const avgScore = metricsMap[k].scores.reduce((a, b) => a + b, 0) / metricsMap[k].scores.length;
          const passed = avgScore >= metricsMap[k].threshold;
          return {
            id: idx + 1,
            key: k.toLowerCase(),
            name: k.replace(/_/g, ' '),
            score: Number(avgScore.toFixed(2)),
            threshold: Number(metricsMap[k].threshold),
            passed,
            status: passed ? 'PASSED' : 'FAILED',
            explanation: `DeepEval automated judge evaluation using ${metricsMap[k].model}.`
          };
        });

        return {
          projectId: Number(projectId),
          metrics: formattedMetrics,
          historyTrends: []
        };
      }
    } catch (e) {
      console.error(`Failed to load evaluation metrics for project ${projectId}`, e);
    }
    return { projectId: Number(projectId), metrics: [], historyTrends: [] };
  }

  // --- OpenTelemetry Traces ---
  async getTraceTree(runId) {
    if (!runId) return null;
    try {
      const data = await this.request(`/traces/${runId}`);
      if (Array.isArray(data) && data.length > 0) {
        const rootRecord = data[0];
        const totalDuration = data.reduce((acc, r) => acc + (r.durationMs || 0), 0);
        const totalTokens = data.reduce((acc, r) => acc + (r.promptTokens || 0) + (r.completionTokens || 0), 0);

        return {
          runId: Number(runId),
          traceId: rootRecord.traceId || `trace-${runId}`,
          totalDurationMs: totalDuration || 0,
          totalTokens: totalTokens || 0,
          status: data.some((r) => r.status === 'BLOCKED') ? 'BLOCKED' : 'COMPLETED',
          spans: data.map((r) => {
            let inputState = {};
            let outputState = {};
            try {
              inputState = typeof r.inputState === 'string' ? JSON.parse(r.inputState || '{}') : r.inputState || {};
            } catch {
              inputState = { raw: r.inputState };
            }
            try {
              outputState = typeof r.outputState === 'string' ? JSON.parse(r.outputState || '{}') : r.outputState || {};
            } catch {
              outputState = { raw: r.outputState };
            }

            return {
              id: r.spanId || `span-${r.id}`,
              parentSpanId: r.parentSpanId,
              name: r.nodeName || 'execution_node',
              type: r.nodeType || 'LANGGRAPH_NODE',
              durationMs: r.durationMs || 0,
              status: r.status || 'COMPLETED',
              inputState,
              outputState,
              tokens: (r.promptTokens || 0) + (r.completionTokens || 0)
            };
          })
        };
      }
    } catch (e) {
      console.error(`Failed to load trace tree for run ${runId}`, e);
    }
    return null;
  }

  // --- Dashboard Summary ---
  async getDashboardSummary(projectId) {
    if (!projectId) return null;
    try {
      const data = await this.request(`/dashboard/summary?projectId=${projectId}`);
      if (data) {
        return {
          totalRuns: data.totalRuns || 0,
          securityFindingsTotal: data.securityFindingsTotal || 0,
          averageLatencyMs: data.averageLatencyMs || 0,
          averageFaithfulnessScore: data.averageFaithfulnessScore || 0,
          securityTestPassRate: data.securityTestPassRate || 0,
          taskSuccessRate: data.taskSuccessRate || 0,
          vulnerabilityRate: data.vulnerabilityRate || 0,
          guardrailMitigationRate: data.guardrailMitigationRate || 0,
          threatDistribution: data.threatDistribution || [],
          findingsBySeverity: data.findingsBySeverity || [],
          recentRuns: data.recentRuns || []
        };
      }
    } catch (e) {
      console.error(`Failed to load dashboard summary for project ${projectId}`, e);
    }
    return null;
  }

  // --- AgentDojo Benchmark Suite ---
  async getAgentDojoSuites() {
    try {
      const data = await this.request('/agentdojo/suites');
      return Array.isArray(data) ? data : [];
    } catch (e) {
      console.error('Failed to load AgentDojo suites', e);
      return [];
    }
  }

  async getAgentDojoScenarios(suite) {
    try {
      const uri = suite && suite !== 'ALL' ? `/agentdojo/scenarios?suite=${suite}` : '/agentdojo/scenarios';
      const data = await this.request(uri);
      return Array.isArray(data) ? data : [];
    } catch (e) {
      console.error(`Failed to load AgentDojo scenarios for suite ${suite}`, e);
      return [];
    }
  }

  async runAgentDojoBenchmark(payload) {
    try {
      return await this.request('/agentdojo/run', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    } catch (e) {
      console.error('Failed to execute AgentDojo benchmark run', e);
      throw e;
    }
  }
}

export const apiService = new ApiService();
export default apiService;
