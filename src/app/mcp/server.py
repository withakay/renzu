"""MCP server construction and runtime helpers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from inspect import Parameter, signature
from typing import Any, cast

from app import __version__
from app.mcp.tools.glass import register_glass_tools
from app.mcp.tools.retrieval import register_retrieval_tools

type FastMCPFactory = Callable[..., Any]
type ToolHandler = Callable[..., Any]


@dataclass(frozen=True, slots=True)
class MCPServerMetadata:
    """Basic MCP server metadata exposed to clients."""

    name: str = "code-context"
    version: str = __version__
    capabilities: dict[str, dict[str, Any]] | None = None

    def resolved_capabilities(self) -> dict[str, dict[str, Any]]:
        if self.capabilities is not None:
            return self.capabilities
        return {"tools": {}}


def _load_fastmcp() -> type[Any]:
    try:
        module = import_module("mcp.server.fastmcp")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "mcp Python SDK is required. Install project dependencies to run MCP server."
        ) from exc
    fastmcp_cls = getattr(module, "FastMCP", None)
    if fastmcp_cls is None:
        raise RuntimeError("mcp Python SDK missing FastMCP class")
    return fastmcp_cls


def create_mcp_server(
    metadata: MCPServerMetadata | None = None,
    fastmcp_factory: FastMCPFactory | None = None,
    streamable_http_path: str | None = None,
) -> Any:
    """Create MCP server instance with required metadata."""
    resolved_metadata = metadata or MCPServerMetadata()
    try:
        factory = fastmcp_factory or _load_fastmcp()
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "mcp Python SDK is required. Install project dependencies to run MCP server."
        ) from exc

    requested_kwargs: dict[str, Any] = {
        "name": resolved_metadata.name,
        "version": resolved_metadata.version,
        "capabilities": resolved_metadata.resolved_capabilities(),
    }
    if streamable_http_path is not None:
        requested_kwargs["streamable_http_path"] = streamable_http_path
    factory_signature = signature(factory)
    supports_var_kwargs = any(
        parameter.kind is Parameter.VAR_KEYWORD
        for parameter in factory_signature.parameters.values()
    )
    if supports_var_kwargs:
        accepted_kwargs = requested_kwargs
    else:
        accepted_kwargs = {
            key: value
            for key, value in requested_kwargs.items()
            if key in factory_signature.parameters
        }

    server = factory(**accepted_kwargs)
    if "version" not in accepted_kwargs:
        server.version = resolved_metadata.version
    if "capabilities" not in accepted_kwargs:
        server.capabilities = resolved_metadata.resolved_capabilities()
    register_retrieval_tools(server=server)
    register_glass_tools(server=server)
    return server


def register_tool(
    *,
    server: Any,
    name: str,
    handler: ToolHandler,
    description: str | None = None,
) -> ToolHandler:
    """Register an MCP tool on a server instance."""
    tool = getattr(server, "tool", None)
    if not callable(tool):
        raise RuntimeError("Provided server does not expose a tool registration API")

    kwargs: dict[str, Any] = {"name": name}
    if description is not None:
        kwargs["description"] = description

    decorator_factory = cast(Callable[..., Callable[[ToolHandler], ToolHandler]], tool)
    decorated = decorator_factory(**kwargs)(handler)
    return decorated


def get_server_info(server: Any) -> dict[str, Any]:
    """Return required MCP server information fields."""
    name = getattr(server, "name", None)
    version = getattr(server, "version", None)
    capabilities = getattr(server, "capabilities", None)

    if name is None and hasattr(server, "init_kwargs"):
        name = server.init_kwargs.get("name")
    if version is None and hasattr(server, "init_kwargs"):
        version = server.init_kwargs.get("version")
    if capabilities is None and hasattr(server, "init_kwargs"):
        capabilities = server.init_kwargs.get("capabilities")

    return {
        "name": str(name),
        "version": str(version),
        "capabilities": capabilities,
    }


def run_stdio_server(server: Any) -> None:
    """Run MCP server over stdio transport."""
    run = getattr(server, "run", None)
    if not callable(run):
        raise RuntimeError("Provided server does not expose a run API")
    run(transport="stdio")


def create_streamable_http_app(server: Any) -> Any:
    """Build a Starlette app for MCP streamable HTTP transport."""
    app_factory = getattr(server, "streamable_http_app", None)
    if not callable(app_factory):
        raise RuntimeError("Provided server does not expose streamable_http_app")
    return app_factory()


def run_streamable_http_server(server: Any, *, mount_path: str = "/mcp") -> None:
    """Run MCP server over streamable HTTP transport."""
    run = getattr(server, "run", None)
    if not callable(run):
        raise RuntimeError("Provided server does not expose a run API")
    run(transport="streamable-http", mount_path=mount_path)
