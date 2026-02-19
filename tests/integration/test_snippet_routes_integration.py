"""Integration tests for snippet HTTP routes.

These tests validate FastAPI wiring and request/response behavior for snippet
fetching without requiring external services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from app.main import app

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.integration
@pytest.mark.asyncio
async def test_snippet_route_supports_context_lines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.api.routes as routes

    routes.clear_repo_roots()

    async def fake_index_repo(*_: object, **__: object) -> tuple[int, int]:
        return (0, 0)

    monkeypatch.setattr(routes, "_index_repo", fake_index_repo)
    monkeypatch.setattr(routes, "get_qdrant_client", lambda: object())

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "hello.txt").write_text("a\nb\nc\nd\n", encoding="utf-8")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        index_response = await client.post(
            "/v1/index",
            json={"repo_id": "test", "path": str(repo_root), "globs": ["**/*.txt"]},
        )
        assert index_response.status_code == 200

        snippet_response = await client.post(
            "/v1/snippet",
            json={
                "repo_id": "test",
                "path": "hello.txt",
                "start_line": 2,
                "end_line": 3,
                "context_lines": 1,
            },
        )

    assert snippet_response.status_code == 200
    payload = snippet_response.json()
    assert payload["ok"] is True
    assert payload["start_line"] == 1
    assert payload["end_line"] == 4
    assert payload["content"] == "a\nb\nc\nd\n"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_snippet_route_returns_404_for_unknown_repo() -> None:
    import app.api.routes as routes

    routes.clear_repo_roots()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/snippet",
            json={"repo_id": "missing", "path": "hello.txt", "start_line": 1, "end_line": 1},
        )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "unknown_repo"
