"""Unit tests for the GlassClient HTTP wrapper."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest


@pytest.mark.unit
class TestGlassClient:
    async def test_list_symbols_success(self) -> None:
        from app.glass.client import GlassClient

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/glass/list_symbols"
            payload: dict[str, Any] = json.loads(request.content.decode("utf-8"))
            assert payload == {"repo_id": "r1", "path": "src/main.py"}
            return httpx.Response(
                200,
                json={
                    "symbols": [
                        {
                            "id": "sym1",
                            "name": "main",
                            "kind": "function",
                            "range": {
                                "start": {"line": 1, "character": 0},
                                "end": {"line": 10, "character": 0},
                            },
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(base_url="http://glass", http_client=http_client)
            symbols = await client.list_symbols("r1", "src/main.py")

        assert len(symbols) == 1
        assert symbols[0].symbol_id == "sym1"
        assert symbols[0].name == "main"
        assert symbols[0].kind == "function"
        assert symbols[0].range is not None
        assert symbols[0].range.start.line == 1

    async def test_describe_symbol_success(self) -> None:
        from app.glass.client import GlassClient

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/glass/describe_symbol"
            payload: dict[str, Any] = json.loads(request.content.decode("utf-8"))
            assert payload == {"symbol_id": "sym1"}
            return httpx.Response(
                200,
                json={
                    "symbol": {"id": "sym1", "name": "main", "kind": "function"},
                    "definition": {
                        "repo_id": "r1",
                        "path": "src/main.py",
                        "range": {
                            "start": {"line": 1, "character": 0},
                            "end": {"line": 1, "character": 10},
                        },
                    },
                },
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(base_url="http://glass", http_client=http_client)
            desc = await client.describe_symbol("sym1")

        assert desc is not None
        assert desc.symbol is not None
        assert desc.symbol.symbol_id == "sym1"
        assert desc.definition is not None
        assert desc.definition.path == "src/main.py"

    async def test_uses_glass_url_from_settings_when_base_url_not_provided(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.config import get_settings
        from app.glass.client import GlassClient

        monkeypatch.setenv("GLASS_URL", "http://glass-from-env")
        get_settings.cache_clear()

        observed_host: str | None = None

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal observed_host
            observed_host = request.url.host
            return httpx.Response(200, json={"symbols": []})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://glass-from-env"
        ) as http_client:
            client = GlassClient(http_client=http_client)
            await client.list_symbols("r1", "src/main.py")

        assert observed_host == "glass-from-env"

    async def test_find_references_success(self) -> None:
        from app.glass.client import GlassClient

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/glass/find_references"
            payload: dict[str, Any] = json.loads(request.content.decode("utf-8"))
            assert payload == {"symbol_id": "sym1"}
            return httpx.Response(
                200,
                json={
                    "references": [
                        {
                            "repo_id": "r1",
                            "path": "src/other.py",
                            "range": {
                                "start": {"line": 5, "character": 2},
                                "end": {"line": 5, "character": 6},
                            },
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(base_url="http://glass", http_client=http_client)
            refs = await client.find_references("sym1")

        assert len(refs) == 1
        assert refs[0].path == "src/other.py"
        assert refs[0].range is not None
        assert refs[0].range.start.line == 5

    async def test_unavailable_returns_empty_when_graceful(self) -> None:
        from app.glass.client import GlassClient

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("no route", request=request)

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(base_url="http://glass", http_client=http_client, graceful=True)
            assert await client.list_symbols("r1", "src/main.py") == []
            assert await client.find_references("sym1") == []
            assert await client.describe_symbol("sym1") is None

    async def test_non_2xx_returns_empty_when_graceful(self) -> None:
        from app.glass.client import GlassClient

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(501, json={"error": "not implemented"})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(base_url="http://glass", http_client=http_client, graceful=True)
            assert await client.list_symbols("r1", "src/main.py") == []

    async def test_unavailable_raises_when_not_graceful(self) -> None:
        from app.glass.client import GlassClient, GlassUnavailableError

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("no route", request=request)

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(base_url="http://glass", http_client=http_client, graceful=False)
            with pytest.raises(GlassUnavailableError):
                await client.list_symbols("r1", "src/main.py")

    async def test_non_2xx_raises_when_not_graceful(self) -> None:
        from app.glass.client import GlassClient, GlassResponseError

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(501, json={"error": "not implemented"})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(base_url="http://glass", http_client=http_client, graceful=False)
            with pytest.raises(GlassResponseError):
                await client.find_references("sym1")

    async def test_returns_empty_when_glass_url_not_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.config import get_settings
        from app.glass.client import GlassClient

        monkeypatch.delenv("GLASS_URL", raising=False)
        get_settings.cache_clear()

        client = GlassClient(graceful=True)
        assert await client.list_symbols("r1", "src/main.py") == []
        assert await client.describe_symbol("sym1") is None
        assert await client.find_references("sym1") == []

    async def test_raises_when_glass_url_not_configured_and_not_graceful(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.config import get_settings
        from app.glass.client import GlassClient, GlassUnavailableError

        monkeypatch.delenv("GLASS_URL", raising=False)
        get_settings.cache_clear()

        client = GlassClient(graceful=False)
        with pytest.raises(GlassUnavailableError):
            await client.describe_symbol("sym1")
