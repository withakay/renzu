"""MCP Glass tools for symbol navigation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, cast

from app.glass.service import (
    GlassResponse,
    SymbolDefinitionRequest,
    SymbolReferencesRequest,
    SymbolsInFileRequest,
    get_glass_service,
)


class GlassToolService(Protocol):
    async def symbols_in_file(self, request: SymbolsInFileRequest) -> GlassResponse: ...

    async def symbol_definition(self, request: SymbolDefinitionRequest) -> GlassResponse: ...

    async def symbol_references(self, request: SymbolReferencesRequest) -> GlassResponse: ...


def _normalize_required(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _register_tool(
    *, server: Any, name: str, description: str, handler: Callable[..., Any]
) -> None:
    tool = getattr(server, "tool", None)
    if not callable(tool):
        raise RuntimeError("Provided server does not expose a tool registration API")
    decorator_factory = cast(
        Callable[..., Callable[[Callable[..., Any]], Callable[..., Any]]], tool
    )
    decorator = decorator_factory(name=name, description=description)
    decorator(handler)


def _model_to_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, dict):
            return cast(dict[str, Any], dumped)
    return None


def _response_base(response: GlassResponse) -> dict[str, Any]:
    return {
        "ok": response.ok,
        "available": response.available,
        "error": response.error,
        "formatted": response.formatted,
    }


def register_glass_tools(
    *,
    server: Any,
    glass_service: GlassToolService | None = None,
    glass_service_getter: Callable[[], GlassToolService] = get_glass_service,
    enabled: bool = True,
) -> None:
    """Register Glass symbol navigation tools on the provided MCP server."""

    if not enabled:
        return

    async def symbols_in_file(repo_id: str, path: str) -> dict[str, Any]:
        normalized_repo_id = _normalize_required(repo_id, field_name="repo_id")
        normalized_path = _normalize_required(path, field_name="path")

        resolved_glass_service = glass_service or glass_service_getter()
        response = await resolved_glass_service.symbols_in_file(
            SymbolsInFileRequest(repo_id=normalized_repo_id, path=normalized_path)
        )

        symbols: list[dict[str, Any]] = []
        if response.ok and isinstance(response.data, list):
            for symbol in cast(list[Any], response.data):
                symbol_dict = _model_to_dict(symbol)
                if symbol_dict is not None:
                    symbols.append(symbol_dict)

        payload = _response_base(response)
        payload.update({"repo_id": normalized_repo_id, "path": normalized_path, "symbols": symbols})
        return payload

    async def symbol_definition(symbol_id: str) -> dict[str, Any]:
        normalized_symbol_id = _normalize_required(symbol_id, field_name="symbol_id")

        resolved_glass_service = glass_service or glass_service_getter()
        response = await resolved_glass_service.symbol_definition(
            SymbolDefinitionRequest(symbol_id=normalized_symbol_id)
        )

        definition = _model_to_dict(response.data) if response.ok else None

        payload = _response_base(response)
        payload.update({"symbol_id": normalized_symbol_id, "definition": definition})
        return payload

    async def symbol_references(symbol_id: str) -> dict[str, Any]:
        normalized_symbol_id = _normalize_required(symbol_id, field_name="symbol_id")

        resolved_glass_service = glass_service or glass_service_getter()
        response = await resolved_glass_service.symbol_references(
            SymbolReferencesRequest(symbol_id=normalized_symbol_id)
        )

        references: list[dict[str, Any]] = []
        if response.ok and isinstance(response.data, list):
            for location in cast(list[Any], response.data):
                location_dict = _model_to_dict(location)
                if location_dict is not None:
                    references.append(location_dict)

        payload = _response_base(response)
        payload.update({"symbol_id": normalized_symbol_id, "references": references})
        return payload

    _register_tool(
        server=server,
        name="symbols_in_file",
        description="List symbols in a repository file",
        handler=symbols_in_file,
    )
    _register_tool(
        server=server,
        name="symbol_definition",
        description="Find the definition location for a symbol",
        handler=symbol_definition,
    )
    _register_tool(
        server=server,
        name="symbol_references",
        description="Find reference locations for a symbol",
        handler=symbol_references,
    )
