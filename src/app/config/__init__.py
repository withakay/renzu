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
    http_port: int = 8000
    log_level: str = "INFO"
    qdrant_collection: str = "code-context"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
