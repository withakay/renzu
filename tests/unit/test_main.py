"""Basic unit tests for the application scaffold."""

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

    def test_readyz_returns_ready(self) -> None:
        from app.main import app

        client = TestClient(app)
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}
