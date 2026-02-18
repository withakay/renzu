"""Unit tests for GlassClient."""

from __future__ import annotations

import json

import httpx
import pytest

from app.glass.client import GlassClient, GlassClientConfig


@pytest.mark.unit
@pytest.mark.asyncio
class TestGlassClient:
    async def test_list_symbols_posts_expected_payload(self) -> None:
        seen: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["method"] = request.method
            seen["path"] = request.url.path
            seen["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(200, json={"symbols": []})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(
                config=GlassClientConfig(base_url="http://glass"), client=http_client
            )
            payload = await client.list_symbols(repo_id="repo-1", path="src/main.py")

        assert payload == {"symbols": []}
        assert seen["method"] == "POST"
        assert seen["path"] == "/v1/glass/list_symbols"
        assert seen["json"] == {"repo_id": "repo-1", "path": "src/main.py"}

    async def test_describe_symbol_posts_expected_payload(self) -> None:
        seen: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["method"] = request.method
            seen["path"] = request.url.path
            seen["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(200, json={"definition": {"symbol_id": "s1", "name": "Foo"}})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(
                config=GlassClientConfig(base_url="http://glass"), client=http_client
            )
            payload = await client.describe_symbol(symbol_id="s1")

        assert payload["definition"]["symbol_id"] == "s1"
        assert seen["method"] == "POST"
        assert seen["path"] == "/v1/glass/describe_symbol"
        assert seen["json"] == {"symbol_id": "s1"}

    async def test_find_references_posts_expected_payload(self) -> None:
        seen: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["method"] = request.method
            seen["path"] = request.url.path
            seen["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(200, json={"references": []})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://glass") as http_client:
            client = GlassClient(
                config=GlassClientConfig(base_url="http://glass"), client=http_client
            )
            payload = await client.find_references(symbol_id="s1")

        assert payload == {"references": []}
        assert seen["method"] == "POST"
        assert seen["path"] == "/v1/glass/find_references"
        assert seen["json"] == {"symbol_id": "s1"}
