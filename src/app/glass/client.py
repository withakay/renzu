"""HTTP client wrapper for the Glass symbol navigation service."""

from __future__ import annotations

import logging
from typing import Any, cast

import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.config import get_settings

logger = logging.getLogger(__name__)


class GlassError(Exception):
    """Base error for Glass client failures."""


class GlassUnavailableError(GlassError):
    """Raised when Glass is unreachable or not configured."""


class GlassResponseError(GlassError):
    """Raised when Glass returns an unexpected or error response."""


class GlassPosition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    line: int
    character: int


class GlassRange(BaseModel):
    model_config = ConfigDict(extra="ignore")

    start: GlassPosition
    end: GlassPosition


class GlassLocation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    repo_id: str | None = None
    path: str
    range: GlassRange | None = None


class GlassSymbol(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    symbol_id: str | None = Field(default=None, alias="id")
    name: str
    kind: str | None = None
    range: GlassRange | None = None
    location: GlassLocation | None = None


class GlassSymbolDescription(BaseModel):
    model_config = ConfigDict(extra="ignore")

    symbol: GlassSymbol | None = None
    definition: GlassLocation | None = None
    signature: str | None = None
    documentation: str | None = None


class GlassClient:
    """Minimal Glass HTTP client.

    This client speaks to a Glass-compatible HTTP service exposing endpoints under
    `/v1/glass/*`.
    """

    _LIST_SYMBOLS_PATH = "/v1/glass/list_symbols"
    _DESCRIBE_PATH = "/v1/glass/describe"
    _FIND_REFERENCES_PATH = "/v1/glass/find_references"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_s: float = 5.0,
        graceful: bool = True,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()
        resolved = base_url if base_url is not None else settings.glass_url
        self._base_url = resolved.rstrip("/") if resolved else None
        self._timeout_s = timeout_s
        self._graceful = graceful
        self._client = http_client
        self._owns_client = http_client is None

    async def __aenter__(self) -> GlassClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
        self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            if self._base_url is None:
                raise GlassUnavailableError("GLASS_URL is not configured")
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout_s)
        return self._client

    async def _post_json(self, path: str, payload: dict[str, Any]) -> Any | None:
        if self._base_url is None:
            if self._graceful:
                logger.info("Glass disabled (GLASS_URL unset); returning empty")
                return None
            raise GlassUnavailableError("GLASS_URL is not configured")

        try:
            client = self._get_client()
            response = await client.post(path, json=payload)
            if response.status_code >= 400:
                message = f"Glass HTTP {response.status_code} for {path}"
                if self._graceful:
                    logger.warning("%s; returning empty", message)
                    return None
                raise GlassResponseError(message)
            return response.json()
        except httpx.TimeoutException as e:
            if self._graceful:
                logger.warning("Glass timeout for %s; returning empty", path)
                return None
            raise GlassUnavailableError("Glass request timed out") from e
        except httpx.RequestError as e:
            if self._graceful:
                logger.warning("Glass request error for %s (%s); returning empty", path, e)
                return None
            raise GlassUnavailableError("Glass request failed") from e
        except ValueError as e:
            if self._graceful:
                logger.warning("Glass invalid JSON for %s; returning empty", path)
                return None
            raise GlassResponseError("Glass returned invalid JSON") from e

    @staticmethod
    def _coerce_list(data: Any, key: str) -> list[dict[str, Any]]:
        source: list[Any]
        if isinstance(data, list):
            source = cast("list[Any]", data)
        elif isinstance(data, dict):
            obj = cast("dict[str, Any]", data)
            value = obj.get(key)
            if not isinstance(value, list):
                return []
            source = cast("list[Any]", value)
        else:
            return []

        result: list[dict[str, Any]] = []
        for item in source:
            if isinstance(item, dict):
                result.append(cast("dict[str, Any]", item))
        return result

    async def list_symbols(self, repo_id: str, path: str) -> list[GlassSymbol]:
        """List symbols for a file path within a repo."""

        data = await self._post_json(self._LIST_SYMBOLS_PATH, {"repo_id": repo_id, "path": path})
        if data is None:
            return []

        items = self._coerce_list(data, "symbols")
        symbols: list[GlassSymbol] = []
        for item in items:
            try:
                symbols.append(GlassSymbol.model_validate(item))
            except Exception:
                logger.debug("Skipping invalid Glass symbol payload: %r", item)
        return symbols

    async def describe_symbol(self, symbol_id: str) -> GlassSymbolDescription | None:
        """Describe a symbol and its definition location."""

        data = await self._post_json(self._DESCRIBE_PATH, {"symbol_id": symbol_id})
        if data is None:
            return None

        if isinstance(data, dict):
            obj = cast("dict[str, Any]", data)
            # Allow either a wrapped response or a flat payload.
            payload: dict[str, Any] = (
                obj if "symbol" in obj or "definition" in obj else {"symbol": obj}
            )
            try:
                return GlassSymbolDescription.model_validate(payload)
            except Exception as e:
                if self._graceful:
                    logger.warning("Glass describe returned unexpected payload; returning empty")
                    return None
                raise GlassResponseError("Unexpected describe_symbol response shape") from e

        if self._graceful:
            logger.warning("Glass describe returned non-object payload; returning empty")
            return None
        raise GlassResponseError("Unexpected describe_symbol response shape")

    async def find_references(self, symbol_id: str) -> list[GlassLocation]:
        """Find references for a symbol."""

        data = await self._post_json(self._FIND_REFERENCES_PATH, {"symbol_id": symbol_id})
        if data is None:
            return []

        items = self._coerce_list(data, "references")
        refs: list[GlassLocation] = []
        for item in items:
            try:
                refs.append(GlassLocation.model_validate(item))
            except Exception:
                logger.debug("Skipping invalid Glass reference payload: %r", item)
        return refs
