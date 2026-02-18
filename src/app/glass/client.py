"""HTTP client for the Glass symbol navigation service."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, cast

import httpx

from app.config import get_settings


class GlassUnavailableError(RuntimeError):
    """Raised when Glass is not configured or cannot be reached."""


@dataclass(frozen=True, slots=True)
class GlassClientConfig:
    base_url: str
    timeout_seconds: float = 5.0


class GlassClient:
    """Minimal async wrapper around the Glass HTTP API."""

    _LIST_SYMBOLS_PATH = "/v1/glass/list_symbols"
    _DESCRIBE_SYMBOL_PATH = "/v1/glass/describe_symbol"
    _FIND_REFERENCES_PATH = "/v1/glass/find_references"
    _HEALTHZ_PATH = "/healthz"

    def __init__(
        self,
        *,
        config: GlassClientConfig,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._config = config
        self._client = client

    @property
    def base_url(self) -> str:
        return self._config.base_url

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client

        timeout = httpx.Timeout(self._config.timeout_seconds)
        self._client = httpx.AsyncClient(base_url=self._config.base_url, timeout=timeout)
        return self._client

    async def aclose(self) -> None:
        if self._client is None:
            return
        await self._client.aclose()

    async def health_check(self) -> bool:
        """Return True when Glass responds to a basic health request."""

        try:
            client = await self._get_client()
            response = await client.get(self._HEALTHZ_PATH)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_symbols(self, repo_id: str, path: str) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.post(
            self._LIST_SYMBOLS_PATH, json={"repo_id": repo_id, "path": path}
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Glass list_symbols response must be an object")
        return cast("dict[str, Any]", payload)

    async def describe_symbol(self, symbol_id: str) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.post(self._DESCRIBE_SYMBOL_PATH, json={"symbol_id": symbol_id})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Glass describe_symbol response must be an object")
        return cast("dict[str, Any]", payload)

    async def find_references(self, symbol_id: str) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.post(self._FIND_REFERENCES_PATH, json={"symbol_id": symbol_id})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Glass find_references response must be an object")
        return cast("dict[str, Any]", payload)


@lru_cache
def get_glass_client() -> GlassClient | None:
    """Return a configured GlassClient or None when disabled."""

    settings = get_settings()
    if not settings.glass_url:
        return None

    return GlassClient(
        config=GlassClientConfig(
            base_url=settings.glass_url,
            timeout_seconds=settings.glass_timeout_seconds,
        )
    )
