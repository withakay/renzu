"""HTTP client for Zoekt lexical search."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, cast

import httpx

from app.config import get_settings

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ZoektClientConfig:
    base_url: str
    timeout_seconds: float = 5.0


@dataclass(frozen=True, slots=True)
class ZoektLineMatch:
    line_number: int
    line: str
    before: str = ""
    after: str = ""
    start_column: int | None = None
    end_column: int | None = None


@dataclass(frozen=True, slots=True)
class ZoektFileMatch:
    repo_id: str
    path: str
    score: float
    line_matches: tuple[ZoektLineMatch, ...]


class ZoektClient:
    """Minimal async wrapper around the Zoekt webserver JSON API."""

    _SEARCH_PATH = "/api/search"
    _HEALTHZ_PATH = "/healthz"
    _INDEX_PATH = "/api/index"

    def __init__(
        self,
        *,
        config: ZoektClientConfig,
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
        try:
            client = await self._get_client()
            response = await client.get(self._HEALTHZ_PATH)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def search(
        self,
        query: str,
        *,
        num: int = 20,
        file_pattern: str | None = None,
    ) -> list[ZoektFileMatch]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must not be empty")
        if num < 1:
            raise ValueError("num must be >= 1")

        zoekt_query = normalized_query
        if file_pattern:
            pattern = file_pattern.strip()
            if pattern:
                zoekt_query = f"{normalized_query} file:{pattern}"

        payload = {"q": zoekt_query, "num": num}

        try:
            client = await self._get_client()
            response = await client.post(self._SEARCH_PATH, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as error:
            logger.warning("Zoekt unavailable for query '%s': %s", normalized_query, error)
            return []

        raw_payload = response.json()
        payload_dict = _as_dict(raw_payload)
        if payload_dict is None:
            raise ValueError("Zoekt search response must be an object")

        result_obj = _as_dict(payload_dict.get("result"))
        if result_obj is None:
            return []

        file_matches_obj = _as_list(result_obj.get("FileMatches"))
        if file_matches_obj is None:
            return []

        matches: list[ZoektFileMatch] = []
        for file_match in file_matches_obj:
            parsed_match = _parse_file_match(file_match)
            if parsed_match is not None:
                matches.append(parsed_match)
        return matches

    async def index_repo(
        self,
        *,
        repo_id: str,
        root: Path,
        changed_files: list[str],
        incremental: bool,
    ) -> None:
        payload = {
            "repo_id": repo_id,
            "root": str(root),
            "changed_files": changed_files,
            "incremental": incremental,
        }
        client = await self._get_client()
        response = await client.post(self._INDEX_PATH, json=payload)
        response.raise_for_status()


def _parse_file_match(payload: object) -> ZoektFileMatch | None:
    payload_dict = _as_dict(payload)
    if payload_dict is None:
        return None

    path = _as_str(payload_dict.get("FileName"))
    repo_id = _as_str(payload_dict.get("Repository"))
    if path is None or repo_id is None:
        return None

    score = _as_float(payload_dict.get("Score")) or 0.0

    line_matches_obj = _as_list(payload_dict.get("LineMatches"))
    parsed_lines: list[ZoektLineMatch] = []
    if line_matches_obj is not None:
        for line_match in line_matches_obj:
            parsed_line = _parse_line_match(line_match)
            if parsed_line is not None:
                parsed_lines.append(parsed_line)

    return ZoektFileMatch(repo_id=repo_id, path=path, score=score, line_matches=tuple(parsed_lines))


def _parse_line_match(payload: object) -> ZoektLineMatch | None:
    payload_dict = _as_dict(payload)
    if payload_dict is None:
        return None

    line_number = _as_int(payload_dict.get("LineNumber"))
    line_text = _as_str(payload_dict.get("Line"))
    if line_number is None or line_text is None:
        return None

    before = _as_str(payload_dict.get("Before")) or ""
    after = _as_str(payload_dict.get("After")) or ""

    start_column: int | None = None
    end_column: int | None = None
    line_fragments = _as_list(payload_dict.get("LineFragments"))
    if line_fragments:
        first_fragment = line_fragments[0]
        fragment_dict = _as_dict(first_fragment)
        if fragment_dict is not None:
            offset = _as_int(fragment_dict.get("LineOffset"))
            length = _as_int(fragment_dict.get("MatchLength"))
            if offset is not None:
                start_column = offset
            if offset is not None and length is not None:
                end_column = offset + length

    return ZoektLineMatch(
        line_number=line_number,
        line=line_text,
        before=before,
        after=after,
        start_column=start_column,
        end_column=end_column,
    )


def _as_dict(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def _as_list(value: object) -> list[object] | None:
    if not isinstance(value, list):
        return None
    return cast(list[object], value)


def _as_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _as_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def _as_float(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


@lru_cache
def get_zoekt_client() -> ZoektClient | None:
    """Return a configured ZoektClient or None when disabled."""

    settings = get_settings()
    if not settings.zoekt_url:
        return None

    return ZoektClient(
        config=ZoektClientConfig(
            base_url=settings.zoekt_url,
            timeout_seconds=settings.zoekt_timeout_seconds,
        )
    )
