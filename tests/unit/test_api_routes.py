"""Unit tests for FastAPI /v1 endpoints."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class FakeAsyncQdrantClient:
    def __init__(self) -> None:
        self._collections: set[str] = set()
        self._points: list[dict[str, Any]] = []

    async def get_collections(self) -> object:
        return SimpleNamespace(
            collections=[SimpleNamespace(name=name) for name in sorted(self._collections)]
        )

    async def create_collection(self, *, collection_name: str, vectors_config: object) -> None:
        _ = vectors_config
        self._collections.add(collection_name)

    async def upsert(self, *, collection_name: str, points: list[object]) -> None:
        _ = collection_name
        for point in points:
            payload = getattr(point, "payload", None)
            vector = getattr(point, "vector", None)
            point_id = getattr(point, "id", None)
            if not isinstance(payload, dict) or not isinstance(vector, list):
                continue
            self._points.append({"id": point_id, "payload": payload, "vector": vector})

    async def delete(self, *, collection_name: str, points_selector: object) -> None:
        _ = collection_name
        _ = points_selector
        self._points.clear()

    async def search(
        self,
        *,
        collection_name: str,
        query_vector: list[float],
        query_filter: object | None,
        limit: int,
    ) -> list[object]:
        _ = collection_name
        _ = query_vector
        if query_filter is not None:
            _ = query_filter

        candidates = self._points

        scored: list[object] = []
        for index, point in enumerate(candidates[:limit]):
            payload = point.get("payload")
            scored.append(
                SimpleNamespace(
                    id=point.get("id"),
                    score=float(1.0 - (index * 0.01)),
                    payload=payload,
                )
            )
        return scored


@pytest.mark.unit
class TestV1Routes:
    def test_index_and_snippet_roundtrip(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.api import routes
        from app.indexing.qdrant import QdrantClient

        routes.clear_repo_roots()

        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "hello.txt").write_text("a\nb\nc\n", encoding="utf-8")

        fake_client = FakeAsyncQdrantClient()
        fake_qdrant = QdrantClient(collection_name="test", vector_size=8, client=fake_client)
        monkeypatch.setattr(routes, "get_qdrant_client", lambda: fake_qdrant)

        from app.main import app

        client = TestClient(app)
        index_response = client.post(
            "/v1/index",
            json={"repo_id": "test", "path": str(repo_root), "globs": ["**/*.txt"]},
        )
        assert index_response.status_code == 200
        assert index_response.json()["ok"] is True
        assert index_response.json()["repo_id"] == "test"

        snippet_response = client.post(
            "/v1/snippet",
            json={"repo_id": "test", "path": "hello.txt", "start_line": 2, "end_line": 3},
        )
        assert snippet_response.status_code == 200
        assert snippet_response.json()["content"] == "b\nc\n"

    def test_search_requires_index_first(self) -> None:
        from app.api import routes

        routes.clear_repo_roots()

        from app.main import app

        client = TestClient(app)
        response = client.post("/v1/search", json={"query": "x", "repo_id": "missing", "top_k": 3})
        assert response.status_code == 404
        assert response.json()["error"] == "unknown_repo"

    def test_invalid_index_path_returns_structured_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.api import routes
        from app.indexing.qdrant import QdrantClient

        routes.clear_repo_roots()

        fake_client = FakeAsyncQdrantClient()
        fake_qdrant = QdrantClient(collection_name="test", vector_size=8, client=fake_client)
        monkeypatch.setattr(routes, "get_qdrant_client", lambda: fake_qdrant)

        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/v1/index", json={"repo_id": "test", "path": "/no/such/path", "globs": []}
        )
        assert response.status_code == 400
        payload = response.json()
        assert payload["error"] == "invalid_root"
        assert "detail" in payload

    def test_glass_list_symbols_returns_response_shape(self) -> None:
        from app.main import app

        client = TestClient(app)
        response = client.post("/v1/glass/list_symbols", json={"repo_id": "x", "path": "main.py"})
        assert response.status_code == 200
        payload = response.json()
        assert "ok" in payload
        assert "available" in payload
        assert "formatted" in payload
