"""Unit tests for MCP server wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from app.glass.service import GlassResponse
from app.retrieval.search import Citation, SearchResult
from app.retrieval.snippet import Snippet
from app.zoekt.client import ZoektFileMatch, ZoektLineMatch

if TYPE_CHECKING:
    from collections.abc import Callable


class _FakeServer:
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs = kwargs
        self.tools: dict[str, Callable[..., Any]] = {}
        self.run_calls: list[dict[str, Any]] = []

    def tool(self, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        name = str(kwargs["name"])

        def _decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[name] = fn
            return fn

        return _decorator

    def run(self, **kwargs: Any) -> None:
        self.run_calls.append(kwargs)


def _build_fake_server(**kwargs: Any) -> _FakeServer:
    return _FakeServer(**kwargs)


class _FakeSearchService:
    async def search(self, *_: object, **__: object) -> list[SearchResult]:
        return [
            SearchResult(
                text="def ping() -> str:\n    return 'pong'\n",
                citation=Citation(
                    repo_id="repo-1",
                    path="src/ping.py",
                    start_line=10,
                    end_line=11,
                    chunk_type="ts:function",
                    score=0.95,
                    language="python",
                    symbol_scip=None,
                ),
            )
        ]


class _FakeSnippetService:
    def fetch_snippet(
        self,
        repo_id: str,
        path: str,
        *,
        start_line: int,
        end_line: int,
        context_lines: int = 0,
    ) -> Snippet:
        _ = context_lines
        return Snippet(
            start_line=start_line,
            end_line=end_line,
            content=f"{repo_id}:{path}:{start_line}-{end_line}",
        )


class _FakeGlassService:
    async def symbols_in_file(self, request: object) -> GlassResponse:
        _ = request
        return GlassResponse(
            ok=True,
            available=True,
            formatted="Symbols in repo-1:src/ping.py",
            data=[
                {
                    "symbol_id": "sym-1",
                    "name": "ping",
                    "kind": "function",
                    "location": {"repo_id": "repo-1", "path": "src/ping.py", "line": 10},
                }
            ],
        )

    async def symbol_definition(self, request: object) -> GlassResponse:
        _ = request
        return GlassResponse(
            ok=True,
            available=True,
            formatted="Definition for sym-1",
            data={
                "symbol_id": "sym-1",
                "name": "ping",
                "kind": "function",
                "location": {"repo_id": "repo-1", "path": "src/ping.py", "line": 10},
            },
        )

    async def symbol_references(self, request: object) -> GlassResponse:
        _ = request
        return GlassResponse(
            ok=True,
            available=True,
            formatted="References for sym-1",
            data=[
                {"repo_id": "repo-1", "path": "src/ping.py", "line": 15},
                {"repo_id": "repo-1", "path": "src/cli.py", "line": 20},
            ],
        )


class _FakeUnavailableGlassService:
    async def symbols_in_file(self, request: object) -> GlassResponse:
        _ = request
        return GlassResponse(
            ok=False,
            available=False,
            error="Glass is disabled (GLASS_URL not configured)",
            formatted="Glass is disabled (GLASS_URL not configured)",
            data=None,
        )

    async def symbol_definition(self, request: object) -> GlassResponse:
        return await self.symbols_in_file(request)

    async def symbol_references(self, request: object) -> GlassResponse:
        return await self.symbols_in_file(request)


class _FakeZoektClient:
    async def search(
        self,
        query: str,
        *,
        num: int = 20,
        file_pattern: str | None = None,
    ) -> list[ZoektFileMatch]:
        _ = query
        _ = num
        _ = file_pattern
        return [
            ZoektFileMatch(
                repo_id="repo-1",
                path="src/ping.py",
                score=0.88,
                line_matches=(
                    ZoektLineMatch(
                        line_number=42,
                        line="def ping() -> str:",
                        start_column=4,
                        end_column=8,
                    ),
                ),
            )
        ]


@pytest.mark.unit
def test_create_server_uses_default_metadata() -> None:
    from app import __version__
    from app.mcp.server import MCPServerMetadata, create_mcp_server

    server = create_mcp_server(
        metadata=MCPServerMetadata(),
        fastmcp_factory=_build_fake_server,
    )

    assert server.init_kwargs["name"] == "code-context"
    assert server.init_kwargs["version"] == __version__
    assert server.init_kwargs["capabilities"] == {"tools": {}}
    assert "code_search" in server.tools
    assert "code_search_lexical" in server.tools
    assert "code_snippet" in server.tools
    assert "symbols_in_file" in server.tools
    assert "symbol_definition" in server.tools
    assert "symbol_references" in server.tools


@pytest.mark.unit
def test_create_server_accepts_streamable_http_path_override() -> None:
    from app.mcp.server import create_mcp_server

    server = create_mcp_server(
        fastmcp_factory=_build_fake_server,
        streamable_http_path="/",
    )

    assert server.init_kwargs["streamable_http_path"] == "/"


@pytest.mark.unit
def test_register_tool_registers_callable() -> None:
    from app.mcp.server import create_mcp_server, register_tool

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    def ping() -> str:
        return "pong"

    register_tool(server=server, name="ping", handler=ping, description="Ping tool")

    assert "ping" in server.tools
    assert server.tools["ping"]() == "pong"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_code_search_tool_returns_results_with_citations() -> None:
    from app.mcp.server import create_mcp_server
    from app.mcp.tools.retrieval import register_retrieval_tools

    server = create_mcp_server(fastmcp_factory=_build_fake_server)
    register_retrieval_tools(
        server=server,
        search_service=_FakeSearchService(),
        snippet_service=_FakeSnippetService(),
    )

    payload = await server.tools["code_search"](
        query="ping",
        repo_id="repo-1",
        path_prefix="src",
        language="python",
        top_k=3,
    )

    assert payload["query"] == "ping"
    assert payload["repo_id"] == "repo-1"
    assert payload["results"][0]["path"] == "src/ping.py"
    assert payload["results"][0]["citation"] == "repo-1:src/ping.py:10-11"
    assert payload["citations"] == ["repo-1:src/ping.py:10-11"]


@pytest.mark.unit
def test_code_snippet_tool_returns_content_with_citation() -> None:
    from app.mcp.server import create_mcp_server
    from app.mcp.tools.retrieval import register_retrieval_tools

    server = create_mcp_server(fastmcp_factory=_build_fake_server)
    register_retrieval_tools(
        server=server,
        search_service=_FakeSearchService(),
        snippet_service=_FakeSnippetService(),
    )

    payload = server.tools["code_snippet"](
        repo_id="repo-1",
        path="src/ping.py",
        start_line=20,
        end_line=30,
    )

    assert payload["content"] == "repo-1:src/ping.py:20-30"
    assert payload["citation"] == "repo-1:src/ping.py:20-30"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_code_search_validates_required_parameters() -> None:
    from app.mcp.server import create_mcp_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    with pytest.raises(ValueError, match="query must not be empty"):
        await server.tools["code_search"](query="   ", repo_id="repo-1")

    with pytest.raises(ValueError, match="repo_id must not be empty"):
        await server.tools["code_search"](query="ping", repo_id=" ")

    with pytest.raises(ValueError, match="top_k must be >= 1"):
        await server.tools["code_search"](query="ping", repo_id="repo-1", top_k=0)

    with pytest.raises(ValueError, match="top_k must be <= 100"):
        await server.tools["code_search"](query="ping", repo_id="repo-1", top_k=101)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_code_search_lexical_tool_formats_results_and_citations() -> None:
    from app.mcp.server import create_mcp_server
    from app.mcp.tools.retrieval import register_retrieval_tools

    server = create_mcp_server(fastmcp_factory=_build_fake_server)
    register_retrieval_tools(
        server=server,
        search_service=_FakeSearchService(),
        snippet_service=_FakeSnippetService(),
        zoekt_client=_FakeZoektClient(),
    )

    payload = await server.tools["code_search_lexical"](
        query="ping AND function",
        repo_id="repo-1",
        file_pattern="*.py",
        top_k=5,
    )

    assert payload["query"] == "ping AND function"
    assert payload["repo_id"] == "repo-1"
    assert payload["results"][0]["path"] == "src/ping.py"
    assert payload["results"][0]["start_line"] == 42
    assert payload["results"][0]["citation"] == "repo-1:src/ping.py:42-42"
    assert payload["citations"] == ["repo-1:src/ping.py:42-42"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_code_search_lexical_reports_unavailability() -> None:
    from app.mcp.server import create_mcp_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    payload = await server.tools["code_search_lexical"](
        query="foo",
        repo_id="repo-1",
    )

    assert payload["results"] == []
    assert payload["error"] is not None
    assert "Zoekt" in payload["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_code_search_lexical_validates_parameters() -> None:
    from app.mcp.server import create_mcp_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    with pytest.raises(ValueError, match="query must not be empty"):
        await server.tools["code_search_lexical"](query=" ", repo_id="repo-1")

    with pytest.raises(ValueError, match="repo_id must not be empty"):
        await server.tools["code_search_lexical"](query="foo", repo_id=" ")


@pytest.mark.unit
def test_code_snippet_validates_parameters() -> None:
    from app.mcp.server import create_mcp_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    with pytest.raises(ValueError, match="repo_id must not be empty"):
        server.tools["code_snippet"](repo_id="", path="x.py", start_line=1, end_line=1)

    with pytest.raises(ValueError, match="path must not be empty"):
        server.tools["code_snippet"](repo_id="r", path="", start_line=1, end_line=1)

    with pytest.raises(ValueError, match="start_line must be >= 1"):
        server.tools["code_snippet"](repo_id="r", path="x.py", start_line=0, end_line=1)

    with pytest.raises(ValueError, match="end_line must be >= start_line"):
        server.tools["code_snippet"](repo_id="r", path="x.py", start_line=3, end_line=2)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_symbols_in_file_tool_returns_symbols() -> None:
    from app.mcp.server import create_mcp_server
    from app.mcp.tools.glass import register_glass_tools

    server = create_mcp_server(fastmcp_factory=_build_fake_server)
    register_glass_tools(server=server, glass_service=_FakeGlassService())

    payload = await server.tools["symbols_in_file"](repo_id="repo-1", path="src/ping.py")

    assert payload["ok"] is True
    assert payload["available"] is True
    assert payload["symbols"][0]["symbol_id"] == "sym-1"
    assert payload["symbols"][0]["location"]["path"] == "src/ping.py"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_symbol_definition_tool_returns_definition() -> None:
    from app.mcp.server import create_mcp_server
    from app.mcp.tools.glass import register_glass_tools

    server = create_mcp_server(fastmcp_factory=_build_fake_server)
    register_glass_tools(server=server, glass_service=_FakeGlassService())

    payload = await server.tools["symbol_definition"](symbol_id="sym-1")

    assert payload["ok"] is True
    assert payload["available"] is True
    assert payload["definition"]["symbol_id"] == "sym-1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_symbol_references_tool_returns_references() -> None:
    from app.mcp.server import create_mcp_server
    from app.mcp.tools.glass import register_glass_tools

    server = create_mcp_server(fastmcp_factory=_build_fake_server)
    register_glass_tools(server=server, glass_service=_FakeGlassService())

    payload = await server.tools["symbol_references"](symbol_id="sym-1")

    assert payload["ok"] is True
    assert payload["available"] is True
    assert len(payload["references"]) == 2
    assert payload["references"][0]["path"] == "src/ping.py"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_glass_tools_unavailability_returns_informative_error() -> None:
    from app.mcp.server import create_mcp_server
    from app.mcp.tools.glass import register_glass_tools

    server = create_mcp_server(fastmcp_factory=_build_fake_server)
    register_glass_tools(server=server, glass_service=_FakeUnavailableGlassService())

    payload = await server.tools["symbols_in_file"](repo_id="repo-1", path="src/ping.py")

    assert payload["ok"] is False
    assert payload["available"] is False
    assert payload["error"] is not None
    assert "disabled" in payload["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_glass_tools_validate_required_parameters() -> None:
    from app.mcp.server import create_mcp_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    with pytest.raises(ValueError, match="repo_id must not be empty"):
        await server.tools["symbols_in_file"](repo_id=" ", path="src/ping.py")

    with pytest.raises(ValueError, match="path must not be empty"):
        await server.tools["symbols_in_file"](repo_id="repo-1", path="")

    with pytest.raises(ValueError, match="symbol_id must not be empty"):
        await server.tools["symbol_definition"](symbol_id=" ")


@pytest.mark.unit
def test_run_stdio_server_uses_stdio_transport() -> None:
    from app.mcp.server import create_mcp_server, run_stdio_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    run_stdio_server(server)

    assert server.run_calls == [{"transport": "stdio"}]


@pytest.mark.unit
def test_run_streamable_http_server_uses_http_transport() -> None:
    from app.mcp.server import create_mcp_server, run_streamable_http_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    run_streamable_http_server(server, mount_path="/mcp")

    assert server.run_calls == [{"transport": "streamable-http", "mount_path": "/mcp"}]


@pytest.mark.unit
def test_create_streamable_http_app_raises_when_missing_factory() -> None:
    from app.mcp.server import create_streamable_http_app

    with pytest.raises(RuntimeError, match="streamable_http_app"):
        create_streamable_http_app(object())


@pytest.mark.unit
def test_server_metadata_response_contains_required_fields() -> None:
    from app.mcp.server import create_mcp_server, get_server_info

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    info = get_server_info(server)

    assert info == {
        "name": "code-context",
        "version": "0.1.0",
        "capabilities": {"tools": {}},
    }


@pytest.mark.unit
def test_create_mcp_server_raises_clear_error_when_sdk_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.mcp import server as server_module

    monkeypatch.setattr(
        server_module,
        "_load_fastmcp",
        lambda: (_ for _ in ()).throw(ModuleNotFoundError("missing")),
    )

    with pytest.raises(RuntimeError, match="mcp Python SDK"):
        server_module.create_mcp_server()
