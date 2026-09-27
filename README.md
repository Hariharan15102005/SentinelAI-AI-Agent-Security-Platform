# SentinelAI — AI Agent Security, Reliability & Observability Platform

[![Java 21](https://img.shields.io/badge/Java-21-orange.svg)](https://openjdk.org/projects/jdk/21/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.3.4-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-purple.svg)](https://vitejs.dev/)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-blue.svg)](https://www.mysql.com/)

**SentinelAI** is an enterprise-grade platform for evaluating, securing, and observing autonomous AI agents (LangGraph, Gemini, OpenAI). It provides automated adversarial red-teaming, real-time Guardrails AI defense policies, DeepEval LLM-as-a-judge reliability scoring, and OpenTelemetry distributed execution trace visualization.

---

## 🏛 Architecture Overview

```mermaid
flowchart TB
    subgraph Frontend ["Frontend Tier (React + Vite :5173)"]
        UI_Dash[Overview Dashboard]
        UI_Studio[Test Studio & Red-Team Hub]
        UI_Findings[Security Findings Explorer]
        UI_Eval[DeepEval Reliability Hub]
        UI_Traces[OpenTelemetry Trace Explorer]
        UI_Comp[Run Comparison (Baseline vs Secured)]
    end

    subgraph Backend ["Backend Orchestrator (Spring Boot 3.3.4 :8080)"]
        AUTH[JWT Security & Auth Controller]
        PROJ[Project & Test Suite Service]
        RUNS[Test Run State Machine]
        TRACES[OpenTelemetry Trace Store]
        CLIENT[Rest Client with W3C Context]
    end

    subgraph AI_Engine ["AI Microservice (FastAPI + Python 3.11 :8000)"]
        GUARD[Guardrails AI Engine]
        GRAPH[LangGraph Autonomous Agent]
        TOOLS[Sandboxed Tools AST, SQL, Vector]
        EVAL[DeepEval Metric Evaluator]
        CHROMA[ChromaDB Knowledge Base]
        GEMINI[Google Gemini Client / Mock Engine]
    end

    subgraph Storage ["Persistence Tier"]
        MYSQL[(MySQL 8.x Database :3306)]
    end

    UI_Studio -->|JWT Bearer REST| AUTH
    AUTH --> PROJ --> RUNS
    RUNS -->|Persist Runs & Findings| MYSQL
    RUNS -->|HTTP + traceparent| CLIENT
    CLIENT -->|X-Internal-Token| GUARD
    GUARD -->|Input Interceptor| GRAPH
    GRAPH --> TOOLS
    GRAPH --> GEMINI
    GRAPH --> EVAL
    EVAL --> CHROMA
    EVAL -->|Return Structured Telemetry| CLIENT
    TRACES -->|GET /traces/runId| UI_Traces
```

---

## 🚀 Key Features

1. **Adversarial Red-Teaming Studio**:
   - Automated evaluation against direct prompt injections, jailbreaks (DAN, Developer Mode), Base64 obfuscated attacks, and destructive tool tampering.
   - Built-in version-controlled adversarial dataset with 18+ synthetic attack vectors and benign controls.
2. **Modular Guardrails AI Engine**:
   - Pre-execution input filters for instruction overrides and jailbreaks.
   - Tool execution gateway enforcing parameter validation, readonly database constraints, and command injection blocks.
   - Real-time PII & Secrets anonymizer using the Luhn algorithm for credit cards, SSN detection, and API key redaction.
3. **DeepEval Reliability Engine**:
   - Automated LLM-as-a-judge evaluation for **Faithfulness**, **Answer Relevancy**, **Hallucination Score**, and custom **G-Eval** criteria.
   - RAG retrieval metrics: **Contextual Precision** and **Contextual Recall** backed by ChromaDB vector storage.
   - Zero-cost deterministic heuristic evaluation for fast automated testing.
4. **OpenTelemetry Distributed Tracing**:
   - End-to-end W3C `traceparent` context propagation across frontend, Spring Boot, and FastAPI.
   - Interactive waterfall timeline displaying node latencies, parent-child span hierarchy, token counts, and input/output states.
5. **Side-by-Side Run Comparison**:
   - Compare `BASELINE` (unprotected) vs. `SECURED` (guardrail-protected) agent runs to measure security containment, latency overhead, and quality score gains.

---

## 🛠 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite 5, React Router 6, Vanilla CSS, Recharts, Lucide Icons |
| **Backend** | Java 21, Spring Boot 3.3.4, Spring Data JPA, Spring Security, JJWT, MySQL 8.x |
| **AI Service** | Python 3.11, FastAPI, LangGraph, LangChain, Google Generative AI, ChromaDB, Pytest |
| **Telemetry** | OpenTelemetry W3C Trace Context (`traceparent`), Structured Spans |

---

## 📋 Prerequisites

- **Java Development Kit (JDK)**: Java 21 or higher
- **Node.js**: v18.0.0 or higher (with npm)
- **Python**: 3.11.x
- **MySQL Server**: 8.0 or higher
- **Operating System**: Windows 10/11 (PowerShell)

---

## ⚙️ Environment Configuration

### 1. Spring Boot Backend (`backend/src/main/resources/application.properties` or environment variables)
```properties
PORT=8080
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sentinelai_db
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
JWT_SECRET=defaultSecretKeyForDevelopmentMustBe32BytesLongSentinelAI!
JWT_EXPIRATION_MS=86400000
AI_SERVICE_URL=http://localhost:8000/api/v1
INTERNAL_SERVICE_SECRET=sentinelai_internal_token_secret_key_2026
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 2. Python AI Service (`ai-service/.env`)
```env
PORT=8000
HOST=0.0.0.0
INTERNAL_SERVICE_SECRET=sentinelai_internal_token_secret_key_2026
GEMINI_API_KEY=your_gemini_api_key_here
DEEPEVAL_JUDGE_MODEL=gemini-1.5-flash
```
*(Note: If `GEMINI_API_KEY` is not provided, the service automatically runs in Mock/Offline mode with deterministic evaluation).*

### 3. React Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8080/api/v1
```

---

## 💻 Local Windows Startup Guide

Open three separate Windows PowerShell terminal windows:

### Terminal 1: Start FastAPI AI Microservice
```powershell
cd "c:\Users\Hariharan K\OneDrive\Desktop\SentinelAI\ai-service"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Health Check*: `http://localhost:8000/api/v1/health`

### Terminal 2: Start Spring Boot Backend
```powershell
cd "c:\Users\Hariharan K\OneDrive\Desktop\SentinelAI\backend"
./mvnw.cmd spring-boot:run
```
*Swagger OpenAPI*: `http://localhost:8080/swagger-ui.html`

### Terminal 3: Start React Frontend
```powershell
cd "c:\Users\Hariharan K\OneDrive\Desktop\SentinelAI\frontend"
npm run dev
```
*Frontend URL*: `http://localhost:5173`

---

## 🧪 Automated Testing

### Run Python AI Service Test Suite (44 Tests):
```powershell
cd "c:\Users\Hariharan K\OneDrive\Desktop\SentinelAI\ai-service"
python -m pytest tests/ -v
```

### Run Spring Boot Backend Test Suite (14 Tests):
```powershell
cd "c:\Users\Hariharan K\OneDrive\Desktop\SentinelAI\backend"
mvn test
```

### Validate React Production Build:
```powershell
cd "c:\Users\Hariharan K\OneDrive\Desktop\SentinelAI\frontend"
npm run build
```

**Total Automated Coverage**: **58 passing unit and integration tests** with **0 build errors**.

---

## 📖 Complete End-to-End Demo Walkthrough

1. **Login & Session Initialization**:
   - Navigate to `http://localhost:5173`. Click **Sign In** or use default demo credentials (`admin` / `password`).
2. **Create Project**:
   - On the **Projects** page, create a project (e.g. `Customer Support Bot`) configuring the system prompt and agent tools.
3. **Execute Test Run in Test Studio**:
   - Select an adversarial test case (e.g. `DAN Persona Hijacking` or `Direct Instruction Override`).
   - Run in **`BASELINE`** mode: observe that the unconstrained agent processes the prompt without active guardrail blocking, flagging `isVulnerable: true`.
   - Run in **`SECURED`** mode: observe that Guardrails AI intercepts the attack, blocks execution, redacts PII, and flags `isVulnerable: false`.
4. **Inspect Security Findings**:
   - Navigate to **Security Findings** to review threat classification, triggered rules, and remediation guidelines.
5. **Inspect DeepEval Reliability Hub**:
   - Review automated quality metrics (Faithfulness, Answer Relevancy, Hallucination Score, G-Eval).
6. **Inspect OpenTelemetry Execution Traces**:
   - Open **Execution Traces** to view the hierarchical trace waterfall, span latencies, and input/output payload states.
7. **Run Comparison**:
   - Navigate to **Run Comparison** to view side-by-side metric deltas and vulnerability mitigation proofs.

---

## 🔒 Security Hardening Notes

- **JWT Auth**: Uses HMAC-SHA256 with 24-hour expiration and strict claim validation.
- **Timing-Attack Protection**: Microservice secret comparison uses `hmac.compare_digest`.
- **Sensitive Data Scrubbing**: Credentials and PII are redacted from traces and model prompts.
- **Tool Sandbox**: Tool execution uses AST-isolated mathematical evaluation, readonly SQL constraints, and path traversal pattern blocks.

---

## 📄 License
SentinelAI is released under the **Apache 2.0 License**.
