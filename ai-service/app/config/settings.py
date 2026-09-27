import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    INTERNAL_SERVICE_SECRET: str = os.getenv("INTERNAL_SERVICE_SECRET", "sentinelai_internal_token_secret_key_2026")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gemini-1.5-flash")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    MOCK_LLM_MODE: bool = os.getenv("MOCK_LLM_MODE", "false").lower() == "true"

    # ChromaDB & RAG Configuration
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
    RAG_COLLECTION_NAME: str = os.getenv("RAG_COLLECTION_NAME", "sentinelai_rag_knowledge_base")
    RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "models/text-embedding-004")
    RAG_DEFAULT_CHUNK_SIZE: int = int(os.getenv("RAG_DEFAULT_CHUNK_SIZE", "300"))
    RAG_DEFAULT_CHUNK_OVERLAP: int = int(os.getenv("RAG_DEFAULT_CHUNK_OVERLAP", "50"))
    RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.35"))

    # Model Context Protocol (MCP) Configuration
    MCP_SERVER_ENABLED: bool = os.getenv("MCP_SERVER_ENABLED", "true").lower() == "true"
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "sentinelai-mcp-server")
    MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    MCP_PROTOCOL_VERSION: str = os.getenv("MCP_PROTOCOL_VERSION", "2024-11-05")
    MCP_MAX_TOOL_CALLS_PER_RUN: int = int(os.getenv("MCP_MAX_TOOL_CALLS_PER_RUN", "5"))
    MCP_TOOL_TIMEOUT_SEC: int = int(os.getenv("MCP_TOOL_TIMEOUT_SEC", "15"))

    # LLM Gateway Configuration
    LLM_GATEWAY_DEFAULT_PROVIDER: str = os.getenv("LLM_GATEWAY_DEFAULT_PROVIDER", "gemini")
    LLM_GATEWAY_TIMEOUT_SEC: int = int(os.getenv("LLM_GATEWAY_TIMEOUT_SEC", "30"))
    LLM_GATEWAY_MAX_RETRIES: int = int(os.getenv("LLM_GATEWAY_MAX_RETRIES", "3"))
    LLM_GATEWAY_RATE_LIMIT_RPM: int = int(os.getenv("LLM_GATEWAY_RATE_LIMIT_RPM", "60"))
    LLM_GATEWAY_RATE_LIMIT_TPM: int = int(os.getenv("LLM_GATEWAY_RATE_LIMIT_TPM", "100000"))
    LLM_GATEWAY_MAX_CONCURRENT: int = int(os.getenv("LLM_GATEWAY_MAX_CONCURRENT", "10"))

settings = Settings()



