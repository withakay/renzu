"""Semantic and fallback chunking utilities for source code."""

from __future__ import annotations

import ast
import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class Chunk:
    """Chunk metadata used for embedding and indexing payloads."""

    text: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    chunk_type: str
    symbol_hint: str | None
    symbol_scip: str | None
    content_hash: str


class Chunker(ABC):
    """Abstract chunker API."""

    @abstractmethod
    def chunk(self, content: str, *, language: str) -> Iterator[Chunk]:
        """Yield chunks for a file."""


class TreeSitterChunker(Chunker):
    """Semantic chunker with line-window fallback for unknown languages."""

    _NON_PYTHON_PATTERNS: ClassVar[dict[str, list[tuple[re.Pattern[str], str]]]] = {
        "rust": [
            (re.compile(r"^\s*(?:pub\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)"), "ts:function"),
            (re.compile(r"^\s*(?:pub\s+)?struct\s+([A-Za-z_][A-Za-z0-9_]*)"), "ts:class"),
        ],
        "go": [
            (
                re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)"),
                "ts:function",
            )
        ],
        "typescript": [
            (re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)"), "ts:function"),
            (re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)"), "ts:class"),
        ],
        "javascript": [
            (re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)"), "ts:function"),
            (re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)"), "ts:class"),
        ],
    }

    def __init__(self, *, max_chunk_bytes: int = 4096, fallback_window_lines: int = 120) -> None:
        self.max_chunk_bytes = max_chunk_bytes
        self.fallback_window_lines = fallback_window_lines

    def chunk(self, content: str, *, language: str) -> Iterator[Chunk]:
        semantic_chunks = list(self._extract_semantic_chunks(content, language=language))
        if not semantic_chunks:
            yield from self._fallback_window_chunks(content)
            return

        for chunk in semantic_chunks:
            yield from self._split_if_needed(chunk)

    def _extract_semantic_chunks(self, content: str, *, language: str) -> Iterator[Chunk]:
        normalized = language.lower()
        if normalized == "python":
            yield from self._extract_python_chunks(content)
            return

        patterns = self._NON_PYTHON_PATTERNS.get(normalized)
        if not patterns:
            return

        line_offsets = self._line_offsets(content)
        lines = content.splitlines(keepends=True)
        for index, line in enumerate(lines, start=1):
            for pattern, chunk_type in patterns:
                match = pattern.match(line)
                if not match:
                    continue
                start_byte, end_byte = self._line_span_to_bytes(
                    line_offsets, start_line=index, end_line=index
                )
                text = lines[index - 1]
                yield self._build_chunk(
                    text=text,
                    start_line=index,
                    end_line=index,
                    start_byte=start_byte,
                    end_byte=end_byte,
                    chunk_type=chunk_type,
                    symbol_hint=match.group(1),
                )

    def _extract_python_chunks(self, content: str) -> Iterator[Chunk]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        line_offsets = self._line_offsets(content)
        lines = content.splitlines(keepends=True)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield self._chunk_from_node(
                    node=node,
                    chunk_type="ts:function",
                    lines=lines,
                    line_offsets=line_offsets,
                    symbol_hint=node.name,
                )
            if isinstance(node, ast.ClassDef):
                yield self._chunk_from_node(
                    node=node,
                    chunk_type="ts:class",
                    lines=lines,
                    line_offsets=line_offsets,
                    symbol_hint=node.name,
                )
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        yield self._chunk_from_node(
                            node=member,
                            chunk_type="ts:method",
                            lines=lines,
                            line_offsets=line_offsets,
                            symbol_hint=member.name,
                        )

    def _chunk_from_node(
        self,
        *,
        node: ast.AST,
        chunk_type: str,
        lines: list[str],
        line_offsets: list[int],
        symbol_hint: str | None,
    ) -> Chunk:
        start_line = getattr(node, "lineno", 1)
        end_line = getattr(node, "end_lineno", start_line)
        start_byte, end_byte = self._line_span_to_bytes(
            line_offsets,
            start_line=start_line,
            end_line=end_line,
        )

        text = "".join(lines[start_line - 1 : end_line])
        return self._build_chunk(
            text=text,
            start_line=start_line,
            end_line=end_line,
            start_byte=start_byte,
            end_byte=end_byte,
            chunk_type=chunk_type,
            symbol_hint=symbol_hint,
        )

    def _fallback_window_chunks(self, content: str) -> Iterator[Chunk]:
        lines = content.splitlines(keepends=True)
        line_offsets = self._line_offsets(content)

        index = 1
        while index <= len(lines):
            end_line = min(index + self.fallback_window_lines - 1, len(lines))
            text = "".join(lines[index - 1 : end_line])
            start_byte, end_byte = self._line_span_to_bytes(
                line_offsets,
                start_line=index,
                end_line=end_line,
            )
            chunk = self._build_chunk(
                text=text,
                start_line=index,
                end_line=end_line,
                start_byte=start_byte,
                end_byte=end_byte,
                chunk_type="fallback:window",
                symbol_hint=None,
            )
            yield from self._split_if_needed(chunk)
            index = end_line + 1

    def _split_if_needed(self, chunk: Chunk) -> Iterator[Chunk]:
        if len(chunk.text.encode("utf-8")) <= self.max_chunk_bytes:
            yield chunk
            return

        lines = chunk.text.splitlines(keepends=True)
        current: list[str] = []
        current_bytes = 0
        current_start_line = chunk.start_line
        current_start_byte = chunk.start_byte

        for line in lines:
            line_bytes = len(line.encode("utf-8"))
            if current and current_bytes + line_bytes > self.max_chunk_bytes:
                text = "".join(current)
                end_line = current_start_line + len(current) - 1
                end_byte = current_start_byte + len(text.encode("utf-8"))
                yield self._build_chunk(
                    text=text,
                    start_line=current_start_line,
                    end_line=end_line,
                    start_byte=current_start_byte,
                    end_byte=end_byte,
                    chunk_type=chunk.chunk_type,
                    symbol_hint=chunk.symbol_hint,
                )
                current_start_line = end_line + 1
                current_start_byte = end_byte
                current = []
                current_bytes = 0

            current.append(line)
            current_bytes += line_bytes

        if current:
            text = "".join(current)
            end_line = current_start_line + len(current) - 1
            end_byte = current_start_byte + len(text.encode("utf-8"))
            yield self._build_chunk(
                text=text,
                start_line=current_start_line,
                end_line=end_line,
                start_byte=current_start_byte,
                end_byte=end_byte,
                chunk_type=chunk.chunk_type,
                symbol_hint=chunk.symbol_hint,
            )

    def _build_chunk(
        self,
        *,
        text: str,
        start_line: int,
        end_line: int,
        start_byte: int,
        end_byte: int,
        chunk_type: str,
        symbol_hint: str | None,
    ) -> Chunk:
        return Chunk(
            text=text,
            start_line=start_line,
            end_line=end_line,
            start_byte=start_byte,
            end_byte=end_byte,
            chunk_type=chunk_type,
            symbol_hint=symbol_hint,
            symbol_scip=None,
            content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )

    def _line_offsets(self, content: str) -> list[int]:
        offsets = [0]
        running = 0
        for line in content.splitlines(keepends=True):
            running += len(line.encode("utf-8"))
            offsets.append(running)
        return offsets

    def _line_span_to_bytes(
        self,
        offsets: list[int],
        *,
        start_line: int,
        end_line: int,
    ) -> tuple[int, int]:
        start_index = max(start_line - 1, 0)
        end_index = min(end_line, len(offsets) - 1)
        return offsets[start_index], offsets[end_index]
