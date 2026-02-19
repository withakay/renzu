"""Unit tests for MCP server wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

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
def test_run_stdio_server_uses_stdio_transport() -> None:
    from app.mcp.server import create_mcp_server, run_stdio_server

    server = create_mcp_server(fastmcp_factory=_build_fake_server)

    run_stdio_server(server)

    assert server.run_calls == [{"transport": "stdio"}]


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
