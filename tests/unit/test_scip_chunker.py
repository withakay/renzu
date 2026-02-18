"""Unit tests for SCIP-aware chunker."""

from __future__ import annotations

import pytest

from app.scip import ScipChunker
from app.scip.parser import ScipDocument, ScipDocumentOccurrence, ScipIndex, ScipRange


def _index_for_occurrences(
    relative_path: str, *, occurrences: list[ScipDocumentOccurrence], language: str = "python"
) -> ScipIndex:
    return ScipIndex(
        metadata_project_root="file:///repo",
        documents=(
            ScipDocument(
                relative_path=relative_path,
                language=language,
                occurrences=tuple(occurrences),
                symbols=tuple({occ.symbol for occ in occurrences if occ.symbol}),
            ),
        ),
        external_symbols=(),
    )


@pytest.mark.unit
class TestScipChunker:
    def test_yields_definition_chunks_when_available(self) -> None:
        content = "def alpha():\n    x = 1\n    return x\n\n"
        symbol = "scip-python pypi pkg 1.0.0 main/alpha()."
        occ = ScipDocumentOccurrence(
            relative_path="src/main.py",
            symbol=symbol,
            roles=frozenset({"definition"}),
            range=ScipRange(start_line=0, start_character=4, end_line=0, end_character=9),
            enclosing_range=ScipRange(start_line=0, start_character=0, end_line=3, end_character=0),
        )

        index = _index_for_occurrences("src/main.py", occurrences=[occ])
        chunker = ScipChunker(index)

        chunks = list(chunker.chunk(content, relative_path="src/main.py", language="python"))

        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk.chunk_type == "scip:def"
        assert chunk.symbol_scip == symbol
        assert chunk.symbol_hint == "alpha"
        assert "def alpha" in chunk.text

    def test_dedupes_identical_definition_spans(self) -> None:
        content = "def alpha():\n    return 1\n"
        symbol = "scip-python pypi pkg 1.0.0 main/alpha()."
        occ1 = ScipDocumentOccurrence(
            relative_path="src/main.py",
            symbol=symbol,
            roles=frozenset({"definition"}),
            range=ScipRange(start_line=0, start_character=4, end_line=0, end_character=9),
            enclosing_range=ScipRange(start_line=0, start_character=0, end_line=2, end_character=0),
        )
        occ2 = ScipDocumentOccurrence(
            relative_path="src/main.py",
            symbol=symbol,
            roles=frozenset({"definition"}),
            range=occ1.range,
            enclosing_range=occ1.enclosing_range,
        )
        index = _index_for_occurrences("src/main.py", occurrences=[occ1, occ2])

        chunks = list(
            ScipChunker(index).chunk(content, relative_path="src/main.py", language="python")
        )
        assert len(chunks) == 1

    def test_falls_back_when_no_definitions_for_file(self) -> None:
        content = "def alpha():\n    return 1\n"
        index = _index_for_occurrences("other.py", occurrences=[])
        chunker = ScipChunker(index)

        chunks = list(chunker.chunk(content, relative_path="src/main.py", language="python"))

        assert chunks
        assert all(chunk.symbol_scip is None for chunk in chunks)

    def test_ignores_local_definition_symbols(self) -> None:
        content = "x = 1\n"
        occ = ScipDocumentOccurrence(
            relative_path="src/main.py",
            symbol="local abc123",
            roles=frozenset({"definition"}),
            range=ScipRange(start_line=0, start_character=0, end_line=0, end_character=1),
            enclosing_range=None,
        )
        index = _index_for_occurrences("src/main.py", occurrences=[occ])

        chunks = list(
            ScipChunker(index).chunk(content, relative_path="src/main.py", language="python")
        )

        assert chunks
        assert all(chunk.symbol_scip is None for chunk in chunks)
