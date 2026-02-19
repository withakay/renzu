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


@pytest.mark.integration
def test_retrieval_tools_registered_with_expected_schema() -> None:
    from app.mcp.server import create_mcp_server

    server = create_mcp_server()

    tools = {tool.name: tool for tool in server._tool_manager.list_tools()}  # pyright: ignore[reportPrivateUsage]
    assert "code_search" in tools
    assert "code_search_lexical" in tools
    assert "code_snippet" in tools
    assert "symbols_in_file" in tools
    assert "symbol_definition" in tools
    assert "symbol_references" in tools

    search_schema = tools["code_search"].parameters
    assert search_schema["type"] == "object"
    assert set(search_schema["required"]) == {"query", "repo_id"}
    assert "top_k" in search_schema["properties"]
    assert search_schema["properties"]["top_k"]["default"] == 10

    lexical_schema = tools["code_search_lexical"].parameters
    assert lexical_schema["type"] == "object"
    assert set(lexical_schema["required"]) == {"query", "repo_id"}
    assert "file_pattern" in lexical_schema["properties"]

    snippet_schema = tools["code_snippet"].parameters
    assert snippet_schema["type"] == "object"
    assert set(snippet_schema["required"]) == {"repo_id", "path", "start_line", "end_line"}
    assert snippet_schema["properties"]["start_line"]["type"] == "integer"
    assert snippet_schema["properties"]["end_line"]["type"] == "integer"

    symbols_schema = tools["symbols_in_file"].parameters
    assert symbols_schema["type"] == "object"
    assert set(symbols_schema["required"]) == {"repo_id", "path"}

    definition_schema = tools["symbol_definition"].parameters
    assert definition_schema["type"] == "object"
    assert set(definition_schema["required"]) == {"symbol_id"}

    references_schema = tools["symbol_references"].parameters
    assert references_schema["type"] == "object"
    assert set(references_schema["required"]) == {"symbol_id"}
