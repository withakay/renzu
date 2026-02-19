"""Configuration management module."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    qdrant_url: str = "http://localhost:6333"

    # Embedding configuration.
    embedding_provider: str = "openai"
    embedding_cache_enabled: bool = True
    embedding_max_batch_size: int = 128
    embedding_requests_per_second: float | None = None

    # Optional OpenAI embedding configuration.
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_timeout_seconds: float = 30.0
    # When unset, the embedder falls back to qdrant_vector_size.
    embedding_vector_size: int | None = None
    # Ollama embedding configuration.
    ollama_url: str = "http://localhost:11434"
    ollama_embedding_model: str = "nomic-embed-text"
    # Maximum number of texts per embeddings request.
    embedding_batch_size: int = 96
    # Minimum delay between embedding requests (0 disables rate limiting).
    embedding_min_interval_seconds: float = 0.0
    # Optional. When unset, Glass integration is disabled and callers must handle fallbacks.
    glass_url: str | None = None
    glass_timeout_seconds: float = 5.0
    http_port: int = 8000
    mcp_port: int = 9000
    log_level: str = "INFO"
    qdrant_collection: str = "code_chunks"
    qdrant_vector_size: int = 1536


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
