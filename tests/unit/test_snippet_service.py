"""Unit tests for snippet retrieval service."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.retrieval import snippet

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.unit
class TestSnippetService:
    def setup_method(self) -> None:
        snippet.clear_repo_roots()
        snippet.get_snippet_service.cache_clear()

    def test_fetch_returns_requested_lines(self, tmp_path: Path) -> None:
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "hello.txt").write_text("a\nb\nc\n", encoding="utf-8")

        snippet.register_repo_root("test", repo_root)
        service = snippet.get_snippet_service()

        content = service.fetch("test", "hello.txt", start_line=2, end_line=3)
        assert content == "b\nc\n"

    def test_path_traversal_is_blocked(self, tmp_path: Path) -> None:
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "hello.txt").write_text("a\n", encoding="utf-8")

        snippet.register_repo_root("test", repo_root)
        service = snippet.get_snippet_service()

        with pytest.raises(snippet.SnippetError) as excinfo:
            service.fetch("test", "../etc/passwd", start_line=1, end_line=1)
        assert excinfo.value.error == "invalid_path"

    def test_invalid_range_is_rejected(self, tmp_path: Path) -> None:
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "hello.txt").write_text("a\n", encoding="utf-8")

        snippet.register_repo_root("test", repo_root)
        service = snippet.get_snippet_service()

        with pytest.raises(snippet.SnippetError) as excinfo:
            service.fetch("test", "hello.txt", start_line=3, end_line=2)
        assert excinfo.value.error == "invalid_range"

    def test_out_of_bounds_range_returns_available_lines(self, tmp_path: Path) -> None:
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "hello.txt").write_text("a\nb\nc\n", encoding="utf-8")

        snippet.register_repo_root("test", repo_root)
        service = snippet.get_snippet_service()

        content = service.fetch("test", "hello.txt", start_line=2, end_line=20)
        assert content == "b\nc\n"
