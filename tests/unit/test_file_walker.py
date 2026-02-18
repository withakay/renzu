"""Unit tests for file walker discovery logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.indexing.walker import FileWalker

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.unit
class TestFileWalker:
    def test_walk_applies_include_and_exclude_globs(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
        (tmp_path / "src" / "test_main.py").write_text("print('test')\n", encoding="utf-8")
        (tmp_path / "src" / "readme.txt").write_text("hello\n", encoding="utf-8")

        walker = FileWalker(include=["**/*.py"], exclude=["**/test_*"])

        found = {info.relative_path for info in walker.walk(tmp_path)}
        assert found == {"src/main.py"}

    def test_detects_language_from_extension(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")
        (tmp_path / "README.unknownext").write_text("x\n", encoding="utf-8")

        walker = FileWalker(include=["**/*"])
        results = {info.relative_path: info.language for info in walker.walk(tmp_path)}

        assert results["main.py"] == "python"
        assert results["README.unknownext"] is None

    def test_includes_file_metadata(self, tmp_path: Path) -> None:
        file_path = tmp_path / "module.py"
        file_path.write_text("print('ok')\n", encoding="utf-8")

        walker = FileWalker(include=["**/*.py"])
        info = next(iter(walker.walk(tmp_path)))

        assert info.size_bytes > 0
        assert info.modified_at is not None

    def test_skips_files_above_max_file_size(self, tmp_path: Path) -> None:
        (tmp_path / "small.py").write_text("x\n", encoding="utf-8")
        (tmp_path / "large.py").write_text("0123456789\n", encoding="utf-8")

        walker = FileWalker(include=["**/*.py"], max_file_size_bytes=3)

        found = [info.relative_path for info in walker.walk(tmp_path)]
        assert found == ["small.py"]

    def test_skips_binary_files(self, tmp_path: Path) -> None:
        (tmp_path / "text.py").write_text("print('ok')\n", encoding="utf-8")
        (tmp_path / "binary.py").write_bytes(b"\x00\x01\x02\x03")

        walker = FileWalker(include=["**/*.py"])

        found = {info.relative_path for info in walker.walk(tmp_path)}
        assert found == {"text.py"}

    def test_respects_gitignore_and_custom_ignore_patterns(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text("*.generated.py\nbuild/\n", encoding="utf-8")
        (tmp_path / "src").mkdir()
        (tmp_path / "build").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
        (tmp_path / "src" / "foo.generated.py").write_text("print('x')\n", encoding="utf-8")
        (tmp_path / "build" / "artifact.py").write_text("print('x')\n", encoding="utf-8")

        walker = FileWalker(include=["**/*.py"], ignore_patterns=["**/artifact.py"])

        found = {info.relative_path for info in walker.walk(tmp_path)}
        assert found == {"src/main.py"}

    def test_skips_symlinks_by_default(self, tmp_path: Path) -> None:
        target = tmp_path / "target.py"
        target.write_text("print('ok')\n", encoding="utf-8")
        symlink = tmp_path / "link.py"
        symlink.symlink_to(target)

        walker = FileWalker(include=["**/*.py"])

        found = {info.relative_path for info in walker.walk(tmp_path)}
        assert found == {"target.py"}

    def test_can_follow_symlinks_when_enabled(self, tmp_path: Path) -> None:
        target = tmp_path / "target.py"
        target.write_text("print('ok')\n", encoding="utf-8")
        symlink = tmp_path / "link.py"
        symlink.symlink_to(target)

        walker = FileWalker(include=["**/*.py"], follow_symlinks=True)

        found = {info.relative_path for info in walker.walk(tmp_path)}
        assert found == {"target.py", "link.py"}
