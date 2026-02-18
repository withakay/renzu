"""Integration tests for file walker with a sample repository layout."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.indexing.walker import FileWalker

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.integration
def test_walks_sample_repo_layout(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".venv/\n*.tmp\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "src" / "helper.ts").write_text("export const v = 1;\n", encoding="utf-8")
    (tmp_path / "src" / "notes.tmp").write_text("tmp\n", encoding="utf-8")
    (tmp_path / ".venv" / "ignored.py").write_text("print('x')\n", encoding="utf-8")

    walker = FileWalker(include=["**/*"], exclude=["**/.venv/**"])

    infos = list(walker.walk(tmp_path))
    paths = {info.relative_path for info in infos}
    languages = {info.relative_path: info.language for info in infos}

    assert "src/main.py" in paths
    assert "src/helper.ts" in paths
    assert "src/notes.tmp" not in paths
    assert ".venv/ignored.py" not in paths
    assert languages["src/main.py"] == "python"
    assert languages["src/helper.ts"] == "typescript"
