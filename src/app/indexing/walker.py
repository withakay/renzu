"""File discovery utilities for indexing workflows."""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class FileInfo:
    """Metadata for a discovered file."""

    path: Path
    relative_path: str
    language: str | None
    size_bytes: int
    modified_at: datetime


class FileWalker:
    """Discover source files with include/exclude and safety filters."""

    _LANGUAGE_BY_EXTENSION: ClassVar[dict[str, str]] = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".kt": "kotlin",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
    }

    def __init__(
        self,
        *,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        ignore_patterns: list[str] | None = None,
        max_file_size_bytes: int | None = None,
        follow_symlinks: bool = False,
    ) -> None:
        self.include = include or ["**/*"]
        self.exclude = exclude or []
        self.ignore_patterns = ignore_patterns or []
        self.max_file_size_bytes = max_file_size_bytes
        self.follow_symlinks = follow_symlinks

    def walk(self, root: Path) -> Iterator[FileInfo]:
        """Walk a repository and yield matching file info entries."""

        root_path = root.resolve()
        gitignore_patterns = self._read_gitignore(root_path)

        for dirpath, _, filenames in os.walk(root_path, followlinks=self.follow_symlinks):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                relative_path = file_path.relative_to(root_path).as_posix()

                if file_path.is_symlink() and not self.follow_symlinks:
                    continue
                if not self._matches_any(relative_path, self.include):
                    continue

                combined_excludes = self.exclude + self.ignore_patterns + gitignore_patterns
                if self._is_ignored(relative_path, combined_excludes):
                    continue

                stat = file_path.stat()
                if self.max_file_size_bytes is not None and stat.st_size > self.max_file_size_bytes:
                    continue
                if self._is_binary(file_path):
                    continue

                yield FileInfo(
                    path=file_path,
                    relative_path=relative_path,
                    language=self.detect_language(file_path),
                    size_bytes=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                )

    def detect_language(self, file_path: Path) -> str | None:
        """Detect source language by extension."""

        return self._LANGUAGE_BY_EXTENSION.get(file_path.suffix.lower())

    def _read_gitignore(self, root: Path) -> list[str]:
        gitignore_path = root / ".gitignore"
        if not gitignore_path.exists():
            return []

        patterns: list[str] = []
        for line in gitignore_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            patterns.append(stripped)
        return patterns

    def _is_binary(self, path: Path) -> bool:
        with path.open("rb") as file_handle:
            chunk = file_handle.read(1024)
        return b"\x00" in chunk

    def _is_ignored(self, relative_path: str, patterns: list[str]) -> bool:
        for pattern in patterns:
            if pattern.endswith("/") and relative_path.startswith(pattern):
                return True
            if self._matches_pattern(relative_path, pattern):
                return True
        return False

    def _matches_any(self, relative_path: str, patterns: list[str]) -> bool:
        return any(self._matches_pattern(relative_path, pattern) for pattern in patterns)

    def _matches_pattern(self, relative_path: str, pattern: str) -> bool:
        normalized = pattern.lstrip("/")
        candidates = [normalized]
        if normalized.startswith("**/"):
            candidates.append(normalized[3:])

        return any(fnmatch.fnmatch(relative_path, candidate) for candidate in candidates)
