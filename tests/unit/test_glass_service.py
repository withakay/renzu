"""Unit tests for GlassService."""

from __future__ import annotations

import httpx
import pytest

from app.glass.client import GlassClient, GlassClientConfig
from app.glass.service import (
    GlassService,
    SymbolDefinitionRequest,
    SymbolReferencesRequest,
    SymbolsInFileRequest,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestGlassService:
    async def test_symbols_in_file_falls_back_when_disabled(self) -> None:
        service = GlassService(client=None)

        response = await service.symbols_in_file(
            SymbolsInFileRequest(repo_id="repo-1", path="src/a.py")
        )

        assert response.ok is False
        assert response.available is False
        assert response.error is not None
        assert "disabled" in response.error

    async def test_symbols_in_file_formats_results(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/glass/list_symbols"
            return httpx.Response(
                200,
                json={
                    "symbols": [
                        {
                            "symbol_id": "s1",
                            "name": "foo",
                            "kind": "function",
                            "location": {"path": "src/a.py", "line": 1, "column": 2},
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(
                config=GlassClientConfig(base_url="http://glass"), client=http_client
            )
            service = GlassService(client=client)
            response = await service.symbols_in_file(
                SymbolsInFileRequest(repo_id="repo-1", path="src/a.py")
            )

        assert response.ok is True
        assert response.available is True
        assert "Symbols in repo-1:src/a.py" in response.formatted
        assert "- foo (function) [s1] @ src/a.py:1:2" in response.formatted

    async def test_symbol_definition_formats_without_location(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/glass/describe_symbol"
            return httpx.Response(200, json={"definition": {"symbol_id": "s1", "name": "Foo"}})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(
                config=GlassClientConfig(base_url="http://glass"), client=http_client
            )
            service = GlassService(client=client)
            response = await service.symbol_definition(SymbolDefinitionRequest(symbol_id="s1"))

        assert response.ok is True
        assert response.available is True
        assert response.formatted == "Definition for s1\n- Foo"

    async def test_symbol_references_falls_back_on_http_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/glass/find_references"
            return httpx.Response(503, json={"error": "boom"})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(
                config=GlassClientConfig(base_url="http://glass"), client=http_client
            )
            service = GlassService(client=client)
            response = await service.symbol_references(SymbolReferencesRequest(symbol_id="s1"))

        assert response.ok is False
        assert response.available is False
        assert response.error is not None
        assert response.formatted
