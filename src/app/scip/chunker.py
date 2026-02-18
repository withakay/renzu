"""SCIP-aware symbol chunking.

This chunker uses parsed SCIP symbol occurrences to extract definition spans and
produce chunks annotated with the SCIP symbol identifier.

Hybrid behavior:

- When definition occurrences exist for the given file, yield chunks for those
  definitions.
- When no definition occurrences exist, fall back to a provided semantic
  chunker (default: TreeSitterChunker).

The module also exposes a small convenience wrapper `chunk_with_scip(...)`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.indexing.chunker import Chunk, TreeSitterChunker
from app.scip.parser import ScipDocumentOccurrence, ScipIndex, ScipRange, parse_symbol_identifier

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class _ScipDefinitionSpan:
    symbol: str
    range: ScipRange


class ScipChunker:
    """Chunker that prefers SCIP definition spans when available."""

    def __init__(
        self,
        index: ScipIndex,
        *,
        max_chunk_bytes: int = 4096,
        fallback: TreeSitterChunker | None = None,
    ) -> None:
        self._index = index
        self._max_chunk_bytes = max_chunk_bytes
        self._fallback = fallback or TreeSitterChunker(max_chunk_bytes=max_chunk_bytes)
        self._definitions_by_file = _definitions_by_file(index)

    def chunk(self, content: str, *, relative_path: str, language: str) -> Iterator[Chunk]:
        """Yield chunks for a file, keyed by the SCIP document relative path."""

        spans = self._definitions_by_file.get(relative_path)
        if not spans:
            yield from self._fallback.chunk(content, language=language)
            return

        line_offsets = _line_offsets(content)
        lines = content.splitlines(keepends=True)

        seen: set[tuple[int, int, str]] = set()
        for span in spans:
            start_byte = _position_to_byte_offset(
                lines,
                line_offsets,
                line=span.range.start_line,
                character=span.range.start_character,
            )
            end_byte = _position_to_byte_offset(
                lines,
                line_offsets,
                line=span.range.end_line,
                character=span.range.end_character,
            )
            if end_byte <= start_byte:
                continue

            key = (start_byte, end_byte, span.symbol)
            if key in seen:
                continue
            seen.add(key)

            text = content.encode("utf-8")[start_byte:end_byte].decode("utf-8", errors="ignore")
            if not text.strip():
                continue

            start_line_1 = span.range.start_line + 1
            end_line_1 = _inclusive_end_line_1_based(span.range)
            chunk = _build_chunk(
                text=text,
                start_line=start_line_1,
                end_line=end_line_1,
                start_byte=start_byte,
                end_byte=end_byte,
                chunk_type="scip:def",
                symbol_hint=_symbol_hint(span.symbol),
                symbol_scip=span.symbol,
            )

            yield from _split_if_needed(
                chunk,
                max_chunk_bytes=self._max_chunk_bytes,
            )


def _definitions_by_file(index: ScipIndex) -> dict[str, tuple[_ScipDefinitionSpan, ...]]:
    output: dict[str, list[_ScipDefinitionSpan]] = {}
    for doc in index.documents:
        spans = [_span_from_occurrence(occ) for occ in doc.occurrences]
        filtered = [span for span in spans if span is not None]
        if not filtered:
            continue

        filtered.sort(key=lambda span: (span.range.start_line, span.range.start_character))
        output[doc.relative_path] = filtered
    return {path: tuple(spans) for path, spans in output.items()}


def chunk_with_scip(
    content: str,
    scip_index: ScipIndex,
    *,
    relative_path: str | None = None,
    language: str | None = None,
    max_chunk_bytes: int = 4096,
    fallback: TreeSitterChunker | None = None,
) -> Iterator[Chunk]:
    """Chunk content using SCIP definition spans when available.

    If `relative_path` is omitted and the index contains exactly one document,
    that document's relative path is used.
    """

    if relative_path is None:
        if len(scip_index.documents) != 1:
            raise ValueError("relative_path is required when SCIP index has multiple documents")
        relative_path = scip_index.documents[0].relative_path

    if language is None:
        if len(scip_index.documents) == 1:
            language = scip_index.documents[0].language or "text"
        else:
            language = "text"

    yield from ScipChunker(
        scip_index,
        max_chunk_bytes=max_chunk_bytes,
        fallback=fallback,
    ).chunk(content, relative_path=relative_path, language=language)


def _span_from_occurrence(occ: ScipDocumentOccurrence) -> _ScipDefinitionSpan | None:
    if not occ.symbol:
        return None
    if "definition" not in occ.roles:
        return None
    if "forward_definition" in occ.roles:
        return None
    if occ.symbol.startswith("local "):
        return None

    span_range = occ.enclosing_range or occ.range
    return _ScipDefinitionSpan(symbol=occ.symbol, range=span_range)


def _symbol_hint(symbol: str) -> str | None:
    try:
        parsed = parse_symbol_identifier(symbol)
    except ValueError:
        return None

    if parsed.local_id is not None:
        return parsed.local_id
    if not parsed.descriptors:
        return None
    return parsed.descriptors[-1].name or None


def _inclusive_end_line_1_based(span: ScipRange) -> int:
    end_line0 = span.end_line
    if span.end_line > span.start_line and span.end_character == 0:
        end_line0 -= 1
    if end_line0 < span.start_line:
        end_line0 = span.start_line
    return end_line0 + 1


def _build_chunk(
    *,
    text: str,
    start_line: int,
    end_line: int,
    start_byte: int,
    end_byte: int,
    chunk_type: str,
    symbol_hint: str | None,
    symbol_scip: str | None,
) -> Chunk:
    return Chunk(
        text=text,
        start_line=start_line,
        end_line=end_line,
        start_byte=start_byte,
        end_byte=end_byte,
        chunk_type=chunk_type,
        symbol_hint=symbol_hint,
        symbol_scip=symbol_scip,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def _split_if_needed(chunk: Chunk, *, max_chunk_bytes: int) -> Iterator[Chunk]:
    if len(chunk.text.encode("utf-8")) <= max_chunk_bytes:
        yield chunk
        return

    lines = chunk.text.splitlines(keepends=True)
    current: list[str] = []
    current_bytes = 0
    current_start_line = chunk.start_line
    current_start_byte = chunk.start_byte

    for line in lines:
        line_bytes = len(line.encode("utf-8"))
        if current and current_bytes + line_bytes > max_chunk_bytes:
            text = "".join(current)
            end_line = current_start_line + len(current) - 1
            end_byte = current_start_byte + len(text.encode("utf-8"))
            yield _build_chunk(
                text=text,
                start_line=current_start_line,
                end_line=end_line,
                start_byte=current_start_byte,
                end_byte=end_byte,
                chunk_type=chunk.chunk_type,
                symbol_hint=chunk.symbol_hint,
                symbol_scip=chunk.symbol_scip,
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
        yield _build_chunk(
            text=text,
            start_line=current_start_line,
            end_line=end_line,
            start_byte=current_start_byte,
            end_byte=end_byte,
            chunk_type=chunk.chunk_type,
            symbol_hint=chunk.symbol_hint,
            symbol_scip=chunk.symbol_scip,
        )


def _line_offsets(content: str) -> list[int]:
    offsets = [0]
    running = 0
    for line in content.splitlines(keepends=True):
        running += len(line.encode("utf-8"))
        offsets.append(running)
    return offsets


def _position_to_byte_offset(
    lines: list[str], offsets: list[int], *, line: int, character: int
) -> int:
    if line < 0:
        return 0
    if line >= len(lines):
        return offsets[-1]

    line_text = lines[line]
    clamped = max(0, min(character, len(line_text)))
    return offsets[line] + len(line_text[:clamped].encode("utf-8"))
