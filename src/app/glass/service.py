"""Service layer for Glass symbol navigation."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, cast

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from app.glass.client import GlassClient, get_glass_client


def _maybe_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _maybe_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None


class Location(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo_id: str | None = None
    path: str
    line: int | None = None
    column: int | None = None


class Symbol(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol_id: str
    name: str
    kind: str | None = None
    location: Location | None = None


class SymbolsInFileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo_id: str
    path: str


class SymbolDefinitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol_id: str


class SymbolReferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol_id: str


class GlassResponse(BaseModel):
    """Standard response wrapper for downstream tools."""

    model_config = ConfigDict(extra="forbid")

    ok: bool
    available: bool
    error: str | None = None
    formatted: str = ""
    data: Any | None = None


@dataclass(slots=True)
class GlassService:
    """High-level typed API around GlassClient with graceful fallbacks."""

    client: GlassClient | None

    def _unavailable(self, message: str) -> GlassResponse:
        return GlassResponse(ok=False, available=False, error=message, formatted=message, data=None)

    async def symbols_in_file(self, request: SymbolsInFileRequest) -> GlassResponse:
        if self.client is None:
            return self._unavailable("Glass is disabled (GLASS_URL not configured)")

        try:
            raw = await self.client.list_symbols(request.repo_id, request.path)
        except (httpx.HTTPError, ValueError) as exc:
            return self._unavailable(f"Glass unavailable: {exc}")

        symbols = _parse_symbols(raw)
        formatted = format_symbols_in_file(request.repo_id, request.path, symbols)
        return GlassResponse(ok=True, available=True, formatted=formatted, data=symbols)

    async def symbol_definition(self, request: SymbolDefinitionRequest) -> GlassResponse:
        if self.client is None:
            return self._unavailable("Glass is disabled (GLASS_URL not configured)")

        try:
            raw = await self.client.describe_symbol(request.symbol_id)
        except (httpx.HTTPError, ValueError) as exc:
            return self._unavailable(f"Glass unavailable: {exc}")

        definition = _parse_definition(raw)
        formatted = format_symbol_definition(request.symbol_id, definition)
        return GlassResponse(ok=True, available=True, formatted=formatted, data=definition)

    async def symbol_references(self, request: SymbolReferencesRequest) -> GlassResponse:
        if self.client is None:
            return self._unavailable("Glass is disabled (GLASS_URL not configured)")

        try:
            raw = await self.client.find_references(request.symbol_id)
        except (httpx.HTTPError, ValueError) as exc:
            return self._unavailable(f"Glass unavailable: {exc}")

        references = _parse_references(raw)
        formatted = format_symbol_references(request.symbol_id, references)
        return GlassResponse(ok=True, available=True, formatted=formatted, data=references)


def _parse_symbols(payload: dict[str, Any]) -> list[Symbol]:
    raw_symbols = payload.get("symbols")
    if raw_symbols is None:
        raw_symbols = payload.get("items", [])

    if not isinstance(raw_symbols, list):
        return []

    symbols: list[Symbol] = []
    for item in cast("list[object]", raw_symbols):
        if not isinstance(item, dict):
            continue

        item_dict = cast("dict[str, Any]", item)

        symbol_id = str(item_dict.get("symbol_id") or item_dict.get("id") or "")
        name = str(item_dict.get("name") or "")
        if not symbol_id or not name:
            continue

        location = None
        raw_loc = item_dict.get("location")
        if isinstance(raw_loc, dict):
            raw_loc_dict = cast("dict[str, Any]", raw_loc)
            if isinstance(raw_loc_dict.get("path"), str):
                location = Location(
                    repo_id=_maybe_str(raw_loc_dict.get("repo_id")),
                    path=raw_loc_dict["path"],
                    line=_maybe_int(raw_loc_dict.get("line")),
                    column=_maybe_int(raw_loc_dict.get("column")),
                )

        try:
            symbols.append(
                Symbol(
                    symbol_id=symbol_id,
                    name=name,
                    kind=(
                        str(item_dict["kind"]) if isinstance(item_dict.get("kind"), str) else None
                    ),
                    location=location,
                )
            )
        except ValidationError:
            continue

    return symbols


def _parse_definition(payload: dict[str, Any]) -> Symbol | None:
    raw = payload.get("definition")
    if raw is None and isinstance(payload.get("symbol"), dict):
        raw = payload.get("symbol")

    if not isinstance(raw, dict):
        return None

    raw_dict = cast("dict[str, Any]", raw)

    symbol_id = str(raw_dict.get("symbol_id") or raw_dict.get("id") or "")
    name = str(raw_dict.get("name") or "")
    if not symbol_id or not name:
        return None

    location = None
    raw_loc = raw_dict.get("location")
    if isinstance(raw_loc, dict):
        raw_loc_dict = cast("dict[str, Any]", raw_loc)
        if isinstance(raw_loc_dict.get("path"), str):
            location = Location(
                repo_id=_maybe_str(raw_loc_dict.get("repo_id")),
                path=raw_loc_dict["path"],
                line=_maybe_int(raw_loc_dict.get("line")),
                column=_maybe_int(raw_loc_dict.get("column")),
            )

    try:
        return Symbol(
            symbol_id=symbol_id,
            name=name,
            kind=(str(raw_dict["kind"]) if isinstance(raw_dict.get("kind"), str) else None),
            location=location,
        )
    except ValidationError:
        return None


def _parse_references(payload: dict[str, Any]) -> list[Location]:
    raw_refs = payload.get("references")
    if raw_refs is None:
        raw_refs = payload.get("locations", [])

    if not isinstance(raw_refs, list):
        return []

    refs: list[Location] = []
    for item in cast("list[object]", raw_refs):
        if not isinstance(item, dict):
            continue
        item_dict = cast("dict[str, Any]", item)
        if not isinstance(item_dict.get("path"), str):
            continue

        try:
            refs.append(
                Location(
                    repo_id=_maybe_str(item_dict.get("repo_id")),
                    path=item_dict["path"],
                    line=_maybe_int(item_dict.get("line")),
                    column=_maybe_int(item_dict.get("column")),
                )
            )
        except ValidationError:
            continue

    return refs


def format_symbols_in_file(repo_id: str, path: str, symbols: list[Symbol]) -> str:
    """Format symbols for simple AI consumption."""

    header = f"Symbols in {repo_id}:{path}"
    if not symbols:
        return f"{header}\n(no symbols)"

    lines: list[str] = [header]
    for symbol in symbols:
        kind = f" ({symbol.kind})" if symbol.kind else ""
        loc = ""
        if symbol.location and symbol.location.line is not None:
            loc = f" @ {symbol.location.path}:{symbol.location.line}"
            if symbol.location.column is not None:
                loc += f":{symbol.location.column}"
        lines.append(f"- {symbol.name}{kind} [{symbol.symbol_id}]{loc}")

    return "\n".join(lines)


def format_symbol_definition(symbol_id: str, definition: Symbol | None) -> str:
    if definition is None:
        return f"Definition for {symbol_id}\n(not found)"

    kind = f" ({definition.kind})" if definition.kind else ""
    loc = ""
    if definition.location and definition.location.line is not None:
        loc = f"{definition.location.path}:{definition.location.line}"
        if definition.location.column is not None:
            loc += f":{definition.location.column}"

    if loc:
        return f"Definition for {symbol_id}\n- {definition.name}{kind} @ {loc}"

    return f"Definition for {symbol_id}\n- {definition.name}{kind}"


def format_symbol_references(symbol_id: str, references: list[Location]) -> str:
    header = f"References for {symbol_id}"
    if not references:
        return f"{header}\n(no references)"

    lines: list[str] = [header]
    for ref in references:
        loc = ref.path
        if ref.line is not None:
            loc += f":{ref.line}"
            if ref.column is not None:
                loc += f":{ref.column}"
        lines.append(f"- {loc}")

    return "\n".join(lines)


@lru_cache
def get_glass_service() -> GlassService:
    """Get a cached service instance."""

    return GlassService(client=get_glass_client())
