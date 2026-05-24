"""Application settings and environment configuration for the local RAG service."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration values for model, persistence, and API behavior."""
    app_name: str = "Local RAG Service"
    model_name: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama3"
    persist_directory: Path = Path("chroma_db")
    chunk_size: int = 500
    chunk_overlap: int = 50
    retriever_k: int = 3
    prompt_template: str = (
        "Use the following pieces of retrieved context to answer the question.\n"
        "If you don't know the answer, say that you don't know.\n\n"
        "Context:\n{context}\n\n"
        "Question:\n{input}\n\n"
        "Answer:"
    )
    cors_origins: list[str] = ["http://localhost:8000"]
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }
