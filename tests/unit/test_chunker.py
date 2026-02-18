"""Unit tests for semantic and fallback chunking."""

from __future__ import annotations

import pytest

from app.indexing.chunker import TreeSitterChunker


@pytest.mark.unit
class TestTreeSitterChunker:
    def test_extracts_python_functions(self) -> None:
        content = """
def alpha():
    return 1

def beta(x):
    return x
"""
        chunker = TreeSitterChunker(max_chunk_bytes=2048)

        chunks = list(chunker.chunk(content, language="python"))

        function_chunks = [chunk for chunk in chunks if chunk.chunk_type == "ts:function"]
        assert len(function_chunks) == 2
        assert function_chunks[0].start_line == 2

    def test_extracts_python_classes(self) -> None:
        content = """
class Greeter:
    def hello(self):
        return \"hi\"
"""
        chunker = TreeSitterChunker(max_chunk_bytes=2048)

        chunks = list(chunker.chunk(content, language="python"))

        class_chunks = [chunk for chunk in chunks if chunk.chunk_type == "ts:class"]
        method_chunks = [chunk for chunk in chunks if chunk.chunk_type == "ts:method"]
        assert len(class_chunks) == 1
        assert len(method_chunks) == 1

    def test_unknown_language_uses_fallback_chunking(self) -> None:
        content = "line1\nline2\nline3\n"
        chunker = TreeSitterChunker(max_chunk_bytes=2048, fallback_window_lines=2)

        chunks = list(chunker.chunk(content, language="unknown"))

        assert len(chunks) >= 2
        assert all(chunk.chunk_type == "fallback:window" for chunk in chunks)

    def test_chunk_contains_required_metadata(self) -> None:
        content = "def one():\n    return 1\n"
        chunker = TreeSitterChunker(max_chunk_bytes=2048)

        chunk = next(iter(chunker.chunk(content, language="python")))

        assert chunk.text
        assert chunk.start_line >= 1
        assert chunk.end_line >= chunk.start_line
        assert chunk.start_byte >= 0
        assert chunk.end_byte > chunk.start_byte
        assert chunk.chunk_type
        assert chunk.symbol_scip is None
        assert chunk.content_hash

    def test_large_chunk_is_split_by_max_chunk_bytes(self) -> None:
        content = "def huge():\n" + "    x = 1\n" * 100
        chunker = TreeSitterChunker(max_chunk_bytes=80)

        chunks = list(chunker.chunk(content, language="python"))

        assert len(chunks) > 1
        assert all(len(chunk.text.encode("utf-8")) <= 80 for chunk in chunks)

    def test_rust_binding_extracts_functions(self) -> None:
        content = 'fn main() {\n    println!("hi");\n}\n'
        chunker = TreeSitterChunker(max_chunk_bytes=2048)

        chunks = list(chunker.chunk(content, language="rust"))

        assert any(chunk.chunk_type == "ts:function" for chunk in chunks)
