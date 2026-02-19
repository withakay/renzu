"""Integration tests for MCP server wiring with the SDK."""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_create_mcp_server_with_sdk_metadata() -> None:
    from app.mcp.server import create_mcp_server, get_server_info

    server = create_mcp_server()

    info = get_server_info(server)

    assert info["name"] == "code-context"
    assert info["version"] == "0.1.0"
    assert isinstance(info["capabilities"], dict)
    assert "tools" in info["capabilities"]


@pytest.mark.integration
def test_register_tool_with_sdk_server() -> None:
    from app.mcp.server import create_mcp_server, register_tool

    server = create_mcp_server()

    def ping() -> str:
        return "pong"

    register_tool(server=server, name="ping", handler=ping, description="Ping tool")

    tool_names = [tool.name for tool in server._tool_manager.list_tools()]  # pyright: ignore[reportPrivateUsage]
    assert "ping" in tool_names
