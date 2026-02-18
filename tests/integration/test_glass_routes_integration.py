"""Integration tests for Glass HTTP routes.

These tests validate FastAPI wiring and request/response behavior for the Glass
service layer. They do not require a real Glass server.
"""

from __future__ import annotations

import httpx
import pytest

from app.glass.client import GlassClient, GlassClientConfig
from app.glass.service import GlassService
from app.main import app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_glass_list_symbols_returns_fallback_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.api.routes as routes

    monkeypatch.setattr(routes, "get_glass_service", lambda: GlassService(client=None))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/glass/list_symbols", json={"repo_id": "repo-1", "path": "src/a.py"}
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["available"] is False
    assert "disabled" in (payload.get("error") or "")
    assert payload["formatted"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_glass_routes_return_success_with_injected_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/glass/list_symbols":
            return httpx.Response(
                200,
                json={
                    "symbols": [
                        {
                            "symbol_id": "s1",
                            "name": "foo",
                            "kind": "function",
                            "location": {"path": "src/a.py", "line": 3, "column": 1},
                        }
                    ]
                },
            )
        if request.url.path == "/v1/glass/describe_symbol":
            return httpx.Response(
                200,
                json={
                    "definition": {
                        "symbol_id": "s1",
                        "name": "Foo",
                        "kind": "class",
                        "location": {"path": "src/a.py", "line": 1, "column": 1},
                    }
                },
            )
        if request.url.path == "/v1/glass/find_references":
            return httpx.Response(
                200,
                json={
                    "references": [
                        {"path": "src/a.py", "line": 10, "column": 2},
                        {"path": "src/b.py", "line": 5},
                    ]
                },
            )
        raise AssertionError(f"Unexpected Glass path: {request.url.path}")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
        injected_client = GlassClient(
            config=GlassClientConfig(base_url="http://glass"), client=http_client
        )
        injected_service = GlassService(client=injected_client)

        import app.api.routes as routes

        monkeypatch.setattr(routes, "get_glass_service", lambda: injected_service)

        asgi_transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=asgi_transport, base_url="http://test") as client:
            list_resp = await client.post(
                "/v1/glass/list_symbols", json={"repo_id": "repo-1", "path": "src/a.py"}
            )
            describe_resp = await client.post("/v1/glass/describe", json={"symbol_id": "s1"})
            refs_resp = await client.post("/v1/glass/find_references", json={"symbol_id": "s1"})

    assert list_resp.status_code == 200
    assert list_resp.json()["ok"] is True
    assert "Symbols in repo-1:src/a.py" in list_resp.json()["formatted"]

    assert describe_resp.status_code == 200
    assert describe_resp.json()["ok"] is True
    assert "Definition for s1" in describe_resp.json()["formatted"]

    assert refs_resp.status_code == 200
    assert refs_resp.json()["ok"] is True
    assert "References for s1" in refs_resp.json()["formatted"]
