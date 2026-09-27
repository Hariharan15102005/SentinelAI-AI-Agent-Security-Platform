# SentinelAI Architecture Specification

## 1. Executive Summary & Objective
**SentinelAI** is an enterprise-grade AI Agent Security, Reliability, and Observability Platform designed to evaluate, test, trace, and monitor autonomous LLM agents (specifically built on LangChain/LangGraph).

As AI agents transition into production systems, they face severe risks:
* **Security Threats**: Prompt injection, jailbreaking, insecure output handling, tool misuse, and data exfiltration.
* **Reliability Issues**: Hallucinations, infinite reasoning loops, context drift, non-deterministic API calling, and unhandled tool failures.
* **Observability Gaps**: Lack of granular step-by-step latency, token cost breakdowns, decision graph execution traces, and safety policy evaluations.

SentinelAI provides a single pane of glass for engineers to:
1. Execute controlled AI agent runs against established security and reliability test suites.
2. Intercept and inspect agent inputs/outputs using Guardrails AI.
3. Automatically score agent performance (hallucination, answer relevancy, faithfulness) using DeepEval.
4. Collect standardized execution traces and spans via OpenTelemetry.
5. Compare baseline (unprotected) vs. secured (guardrail-protected) agent runs side-by-side.

---

## 2. Technology Stack & Component Responsibilities

| Tier | Technology | Key Responsibilities |
| :--- | :--- | :--- |
| **Frontend UI** | React.js (Vite, JavaScript), Recharts, Vanilla CSS | Interactive dashboard, test run triggers, live execution telemetry graphs, security findings explorer, evaluation metric visualizations, side-by-side run comparisons. |
| **Backend API Gateway** | Java 21, Spring Boot 3.x, Maven, Spring Data JPA | Central orchestrator, REST API gateway, JWT authentication & authorization (Spring Security), persistence of test suites/runs/results, async dispatching of execution requests to AI Service. |
| **Database** | MySQL 8.x | Relational storage for users, projects, test cases, test execution runs, security findings, evaluation metrics, and granular trace records. |
| **AI Engine & Agent** | Python 3.11+, FastAPI, LangChain, LangGraph | Autonomous agent execution sandbox, graph state machine, tool invocation, Guardrails AI interception, DeepEval metrics computation, OpenTelemetry trace instrumentation. |
| **AI Guardrails** | Guardrails AI | Input sanitization, prompt injection detection, PII masking, toxic output filtering, schema validation. |
| **AI Evaluation** | DeepEval | LLM-as-a-judge automated evaluation (hallucination metric, faithfulness, answer relevancy, contextual precision). |
| **Observability** | OpenTelemetry (Python OTel SDK) | Distributed trace collection, span creation per graph node/LLM call/tool execution, duration and token accounting. |

---

## 3. High-Level System Architecture

```mermaid
flowchart TB
    subgraph Client["Presentation Layer (Client)"]
        UI["React + Vite Frontend\n(Recharts, Modern Dashboard)"]
    end

    subgraph BackendLayer["Core Orchestration Layer (Spring Boot)"]
        Security["Spring Security\n(JWT Auth & RBAC)"]
        Controller["REST Controllers\n(Projects, Tests, Runs, Metrics)"]
        Service["Orchestration Services\n(RunManager, ReportEngine)"]
        Repo["Spring Data JPA\nRepositories"]
        ClientService["AI Service REST Client\n(RestClient / WebClient)"]
    end

    subgraph DatabaseLayer["Persistence Layer"]
        MySQL[(MySQL 8.x Database\nUsers, Projects, Runs, Findings, Traces)]
    end

    subgraph AIServiceLayer["AI Execution & Analysis Engine (FastAPI)"]
        FastAPIEndpoint["FastAPI REST Router\n(/agent/run, /security/scan, /eval/run)"]
        AuthMiddleware["Service Token Validator\n(X-Internal-Token)"]
        
        subgraph AgentSandbox["LangGraph Agent Sandbox"]
            StateGraph["LangGraph StateGraph Engine"]
            AgentNodes["Agent Reasoning Nodes & Tools"]
        end

        subgraph SafetyObservability["Security & Observability Modules"]
            Guardrails["Guardrails AI Engine\n(Input/Output Interceptors)"]
            DeepEvalEngine["DeepEval Evaluator\n(Hallucination & Faithfulness)"]
            OTelTracer["OpenTelemetry Tracer\n(Span & Trace Exporter)"]
        end
    end

    subgraph ExternalLLM["External LLM Providers"]
        Gemini["Google Gemini / LLM APIs"]
    end

    %% Interactions
    UI -->|HTTP / REST (JWT Auth)| Security
    Security --> Controller
    Controller --> Service
    Service --> Repo
    Repo --> MySQL
    Service --> ClientService
    ClientService -->|Internal REST (Service Secret)| FastAPIEndpoint
    FastAPIEndpoint --> AuthMiddleware
    AuthMiddleware --> StateGraph
    StateGraph --> Guardrails
    Guardrails --> AgentNodes
    AgentNodes --> Gemini
    AgentNodes --> OTelTracer
    FastAPIEndpoint --> DeepEvalEngine
    DeepEvalEngine --> Gemini
    FastAPIEndpoint -.->|Execution Result + Traces + Findings + Scores| ClientService
```

---

## 4. Component Interaction and Request Flow

### 4.1 End-to-End Test Execution Flow
1. **Trigger**: The user selects a Test Suite or initiates a run in the React UI (e.g., *Prompt Injection Attack Test* against the customer support agent).
2. **Authentication & Validation**: The request hits Spring Boot with a JWT bearer token. `Spring Security` validates user identity and project permissions.
3. **Run Initialization**: Spring Boot creates a `TestRun` entry in MySQL with status `RUNNING`.
4. **AI Service Invocation**: Spring Boot calls the FastAPI endpoint `POST /api/v1/agent/run` with the payload (agent configuration, guardrails configuration, test input prompt, expected context).
5. **Security Pre-Execution (Guardrails AI)**:
   - If guardrails are enabled, Guardrails AI scans the input prompt for prompt injections, toxic patterns, or jailbreaks.
   - If a violation is caught, a `SecurityFinding` is logged.
6. **Agent Execution (LangGraph)**:
   - LangGraph executes the state graph (reasoning steps, tool calls, LLM queries).
   - `OpenTelemetry` captures spans for every node execution, tool call duration, token consumption, and status.
7. **Security Post-Execution (Guardrails AI)**:
   - Agent outputs and tool responses are validated against security policies (e.g., PII detection, hallucinated system prompts).
8. **Automated Evaluation (DeepEval)**:
   - DeepEval computes automated metrics such as Faithfulness, Answer Relevancy, and Hallucination score against the agent input, retrieved context, and generated output.
9. **Result Aggregation**: FastAPI compiles the execution record, OpenTelemetry trace spans, security findings, and DeepEval scores into a single structured response and returns it to Spring Boot.
10. **Persistence & Presentation**: Spring Boot persists the `TestRun`, `SecurityFinding`, `EvaluationResult`, and `ExecutionRecord` entities in MySQL. The React frontend fetches and renders the updated metrics, interactive trace timeline, and risk assessment radar charts.

---

## 5. Subsystem Responsibilities

### 5.1 Frontend (React + Vite)
* Modern responsive dark/light cybersecurity-themed UI.
* **Test Studio**: Interactive prompt and scenario runner for baseline vs. secured agent testing.
* **Security & Vulnerability Dashboard**: Visual bar/radar charts displaying injection vulnerability rates, guardrail block counts, and risk severity distribution.
* **Evaluation & Reliability Hub**: DeepEval score cards (Faithfulness, Hallucination, Relevancy trends over runs).
* **Observability Waterfall**: OpenTelemetry execution span timeline showing node latency, tool calling sequence, and error points.
* **Comparison View**: Side-by-side run comparison showing how adding guardrails impacted response safety, latency, and evaluation score.

### 5.2 Backend Orchestrator (Spring Boot + Java 21)
* **API Gateway & Auth**: Manages user registration, login, JWT token issuance, and project access controls.
* **Project & Test Suite Management**: CRUD operations for test suites, attack scenarios, baseline configurations, and custom evaluation criteria.
* **Execution Orchestrator**: Manages test execution state machine (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`).
* **Reporting & Analytics Aggregator**: Computes aggregated security pass/fail rates, mean latency, token consumption trends, and overall reliability indices for dashboard consumption.
* **Reliable HTTP Client**: Connects to the FastAPI service using Spring 6 `RestClient` with timeout handling and error encapsulation.

### 5.3 AI Engine (FastAPI + LangChain + LangGraph)
* **LangGraph Agent Implementation**: Modular state graph with tools (e.g., Mock Database Query Tool, API Lookup Tool, Calculator Tool) representing real-world autonomous workflows.
* **Guardrails AI Integration**: Pluggable guardrail layers (Input Guards: prompt injection detection, PII anonymization; Output Guards: toxic speech, structure adherence, secret leakage).
* **DeepEval Integration**: Evaluation pipelines executing automated LLM-judged criteria (Hallucination Metric, Faithfulness Metric, Answer Relevancy).
* **OpenTelemetry Instrumentation**: Custom Span processors collecting execution node details, latency, LLM model parameters, token input/output, and tool parameters.
* **Stateless REST Execution API**: Clean endpoints decoupling agent execution logic from persistence and authorization.

---

## 6. Security Architecture

1. **Authentication & Authorization**:
   - User authentication via JWT (JSON Web Tokens) with standard expiration and refresh mechanisms.
   - Project-level data isolation ensuring users only access test runs for their authorized projects.
2. **Service-to-Service Security**:
   - FastAPI endpoints are protected by an internal shared secret (`X-Internal-Token`) verified on every inbound request from Spring Boot.
3. **Secret & Key Management**:
   - All external API keys (e.g., Google Gemini API key) and database credentials are stored in environment variables, never committed to version control.
4. **Sandboxed Agent Execution**:
   - Agent tool actions are strictly scoped; tool execution runs in controlled simulated environments to avoid arbitrary local code execution.

---

## 7. Local Development Approach (No Docker)

SentinelAI is architected for frictionless local development directly on Windows:
* **Frontend**: Runs on Node.js 18+ via `npm run dev` (Port 5173).
* **Backend**: Runs on Java 21 (JDK 21) via `./mvnw spring-boot:run` (Port 8080).
* **AI Service**: Runs on Python 3.11+ via `uvicorn app.main:app --reload --port 8000`.
* **Database**: Local MySQL 8.x instance running as a standard Windows service (Port 3306).

All services configure their connection strings and shared secrets via distinct `.env` and `application.properties` configuration files.
