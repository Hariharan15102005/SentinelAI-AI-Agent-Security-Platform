from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config.settings import settings

app = FastAPI(
    title="SentinelAI - AI Engine & LangGraph Agent Sandbox",
    description="Python FastAPI Microservice powering autonomous LangGraph agents, Guardrails interception, and DeepEval metrics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "service": "SentinelAI - AI Execution & Observability Engine",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
