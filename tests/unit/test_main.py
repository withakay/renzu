"""Unit tests for health endpoints and configuration."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestHealthEndpoints:
    def test_healthz_returns_ok(self) -> None:
        from app.main import app

        client = TestClient(app)
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_readyz_returns_200_when_dependencies_healthy(self) -> None:
        from app.dependencies import HealthStatus
        from app.main import app

        async def mock_check() -> tuple[bool, list[HealthStatus]]:
            return (True, [HealthStatus(healthy=True, name="qdrant")])

        with patch("app.main.check_all_dependencies", side_effect=mock_check):
            client = TestClient(app)
            response = client.get("/readyz")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["checks"]["qdrant"]["healthy"] is True

    def test_readyz_returns_503_when_dependencies_unhealthy(self) -> None:
        from app.dependencies import HealthStatus
        from app.main import app

        async def mock_check() -> tuple[bool, list[HealthStatus]]:
            return (
                False,
                [HealthStatus(healthy=False, name="qdrant", detail="Connection refused")],
            )

        with patch("app.main.check_all_dependencies", side_effect=mock_check):
            client = TestClient(app)
            response = client.get("/readyz")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "not_ready"
            assert data["checks"]["qdrant"]["healthy"] is False
            assert data["checks"]["qdrant"]["detail"] == "Connection refused"


@pytest.mark.unit
class TestConfig:
    def test_settings_defaults(self) -> None:
        from app.config import Settings

        settings = Settings()
        assert settings.qdrant_url == "http://localhost:6333"
        assert settings.glass_url is None
        assert settings.http_port == 8000
        assert settings.mcp_port == 9000
        assert settings.log_level == "INFO"
        assert settings.qdrant_collection == "code-context"

    def test_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.config import Settings

        monkeypatch.setenv("QDRANT_URL", "http://qdrant:6333")
        monkeypatch.setenv("GLASS_URL", "http://glass:12346")
        monkeypatch.setenv("HTTP_PORT", "9000")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()
        assert settings.qdrant_url == "http://qdrant:6333"
        assert settings.glass_url == "http://glass:12346"
        assert settings.http_port == 9000
        assert settings.log_level == "DEBUG"


@pytest.mark.unit
class TestCorrelationIdMiddleware:
    def test_correlation_id_generated_if_not_provided(self) -> None:
        from app.main import app

        client = TestClient(app)
        response = client.get("/healthz")
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        assert len(response.headers["X-Correlation-ID"]) == 36

    def test_correlation_id_preserved_if_provided(self) -> None:
        from app.main import app

        client = TestClient(app)
        test_id = "test-correlation-123"
        response = client.get("/healthz", headers={"X-Correlation-ID": test_id})
        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == test_id
