"""Snippet retrieval service.

Provides safe access to repository-relative file spans for citations.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class SnippetError(Exception):
    """Raised when snippet retrieval fails."""

    error: str
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class Snippet:
    """A fetched snippet span.

    start_line/end_line are 1-based and inclusive.
    """

    start_line: int
    end_line: int
    content: str


_repo_roots: dict[str, Path] = {}


def clear_repo_roots() -> None:
    """Clear in-memory repo root mappings.

    Intended for tests.
    """

    _repo_roots.clear()


def register_repo_root(repo_id: str, root: Path) -> None:
    """Register a repository root directory for a repo_id."""

    normalized_repo_id = repo_id.strip()
    if not normalized_repo_id:
        raise SnippetError(error="invalid_repo_id", detail="repo_id must not be empty")

    root_path = Path(root).expanduser().resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise SnippetError(error="invalid_root", detail="root must be an existing directory")

    _repo_roots[normalized_repo_id] = root_path


def resolve_repo_root(repo_id: str) -> Path:
    normalized_repo_id = repo_id.strip()
    if not normalized_repo_id:
        raise SnippetError(error="invalid_repo_id", detail="repo_id must not be empty")

    root = _repo_roots.get(normalized_repo_id)
    if root is None:
        raise SnippetError(
            error="unknown_repo",
            detail=f"Unknown repo_id: {normalized_repo_id}. Call POST /v1/index first.",
        )
    return root


def _safe_join(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise SnippetError(error="invalid_path", detail="Path escapes repo root") from exc
    return candidate


class SnippetService:
    """Fetch repository-relative file spans safely."""

    def __init__(
        self,
        *,
        repo_root_resolver: Callable[[str], Path] | None = None,
    ) -> None:
        self._resolve_root = repo_root_resolver or resolve_repo_root

    def fetch_snippet(
        self,
        repo_id: str,
        path: str,
        *,
        start_line: int,
        end_line: int,
        context_lines: int = 0,
    ) -> Snippet:
        """Fetch file content for the given inclusive line range.

        When context_lines > 0, the returned content includes that many extra
        lines of context before start_line and after end_line (clamped to file
        bounds). The returned start/end reflect the expanded range.
        """

        normalized_path = path.strip()
        if not normalized_path:
            raise SnippetError(error="invalid_path", detail="path must not be empty")
        if "\x00" in normalized_path:
            raise SnippetError(error="invalid_path", detail="path contains NUL byte")

        if start_line < 1 or end_line < 1:
            raise SnippetError(error="invalid_range", detail="line numbers must be >= 1")
        if end_line < start_line:
            raise SnippetError(error="invalid_range", detail="end_line must be >= start_line")
        if context_lines < 0:
            raise SnippetError(error="invalid_context", detail="context_lines must be >= 0")

        root = self._resolve_root(repo_id)
        file_path = _safe_join(root, normalized_path)
        if not file_path.exists() or not file_path.is_file():
            raise SnippetError(error="not_found", detail="File not found")

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
        except UnicodeDecodeError as exc:
            raise SnippetError(error="binary_file", detail="File is not UTF-8 text") from exc
        except OSError as exc:
            raise SnippetError(error="read_failed", detail=str(exc)) from exc

        expanded_start = max(start_line - context_lines, 1)
        expanded_end = end_line + context_lines

        start_index = min(max(expanded_start - 1, 0), len(lines))
        end_index = min(expanded_end, len(lines))
        content = "".join(lines[start_index:end_index])

        return Snippet(start_line=expanded_start, end_line=expanded_end, content=content)

    def fetch(
        self,
        repo_id: str,
        path: str,
        *,
        start_line: int,
        end_line: int,
        context_lines: int = 0,
    ) -> str:
        return self.fetch_snippet(
            repo_id,
            path,
            start_line=start_line,
            end_line=end_line,
            context_lines=context_lines,
        ).content


@lru_cache
def get_snippet_service() -> SnippetService:
    return SnippetService()
