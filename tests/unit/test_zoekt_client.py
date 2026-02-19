"""Unit tests for ZoektClient."""

from __future__ import annotations

import json

import httpx
import pytest

from app.zoekt.client import ZoektClient, ZoektClientConfig


@pytest.mark.unit
@pytest.mark.asyncio
class TestZoektClient:
    async def test_search_posts_expected_payload_and_parses_matches(self) -> None:
        seen: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["method"] = request.method
            seen["path"] = request.url.path
            seen["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                200,
                json={
                    "result": {
                        "FileMatches": [
                            {
                                "Repository": "repo-1",
                                "FileName": "src/main.py",
                                "Score": 0.75,
                                "LineMatches": [
                                    {
                                        "LineNumber": 12,
                                        "Line": "def ping():",
                                        "Before": "",
                                        "After": "",
                                        "LineFragments": [{"LineOffset": 4, "MatchLength": 4}],
                                    }
                                ],
                            }
                        ]
                    }
                },
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://zoekt") as http_client:
            client = ZoektClient(
                config=ZoektClientConfig(base_url="http://zoekt"),
                client=http_client,
            )
            matches = await client.search("ping")

        assert len(matches) == 1
        assert matches[0].repo_id == "repo-1"
        assert matches[0].path == "src/main.py"
        assert matches[0].line_matches[0].line_number == 12
        assert matches[0].line_matches[0].start_column == 4
        assert matches[0].line_matches[0].end_column == 8
        assert seen["method"] == "POST"
        assert seen["path"] == "/api/search"
        assert seen["json"] == {"q": "ping", "num": 20}

    async def test_search_supports_boolean_regex_and_file_pattern_query(self) -> None:
        seen: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(200, json={"result": {"FileMatches": []}})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://zoekt") as http_client:
            client = ZoektClient(
                config=ZoektClientConfig(base_url="http://zoekt"),
                client=http_client,
            )
            matches = await client.search("func\\w+ AND reactor", file_pattern="*.py")

        assert matches == []
        assert seen["json"] == {"q": "func\\w+ AND reactor file:*.py", "num": 20}

    async def test_search_returns_empty_on_unavailable_server(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("down", request=request)

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="http://zoekt") as http_client:
            client = ZoektClient(
                config=ZoektClientConfig(base_url="http://zoekt"),
                client=http_client,
            )
            matches = await client.search("ping")

        assert matches == []

    async def test_search_validates_parameters(self) -> None:
        client = ZoektClient(config=ZoektClientConfig(base_url="http://zoekt"))

        with pytest.raises(ValueError, match="query must not be empty"):
            await client.search(" ")

        with pytest.raises(ValueError, match="num must be >= 1"):
            await client.search("ping", num=0)


@pytest.mark.unit
def test_get_zoekt_client_uses_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import get_settings
    from app.zoekt.client import get_zoekt_client

    monkeypatch.setenv("ZOEKT_URL", "http://zoekt:6070")
    monkeypatch.setenv("ZOEKT_TIMEOUT_SECONDS", "7.5")

    get_settings.cache_clear()
    get_zoekt_client.cache_clear()
    try:
        client = get_zoekt_client()
        assert client is not None
        assert client.base_url == "http://zoekt:6070"
    finally:
        get_zoekt_client.cache_clear()
        get_settings.cache_clear()
