"""Integration tests for SCIP parsing + chunking."""

from __future__ import annotations

from typing import Any

import pytest

from app.scip import ScipChunker, chunk_with_scip
from app.scip._proto import scip_pb2
from app.scip.parser import ScipParser

# NOTE: `scip_pb2.py` is generated and builds message classes dynamically.
# Static type checkers do not reliably see the message attributes. Use dynamic
# lookups and `Any` to keep type checking strict elsewhere.
_IndexMessage = getattr(scip_pb2, "Index")  # noqa: B009


@pytest.mark.integration
def test_parsed_scip_index_produces_definition_chunks() -> None:
    content = "def alpha():\n    return 1\n"
    symbol = "scip-python pypi pkg 1.0.0 main/alpha()."

    index: Any = _IndexMessage()
    index.metadata.project_root = "file:///repo"

    doc: Any = index.documents.add()
    doc.relative_path = "src/main.py"
    doc.language = "python"

    occ: Any = doc.occurrences.add()
    occ.symbol = symbol
    occ.symbol_roles = 0x1
    occ.range.extend([0, 4, 0, 9])
    occ.enclosing_range.extend([0, 0, 2, 0])

    sym: Any = doc.symbols.add()
    sym.symbol = symbol

    parsed = ScipParser().parse_bytes(index.SerializeToString())
    chunks = list(
        ScipChunker(parsed).chunk(content, relative_path="src/main.py", language="python")
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_type == "scip:def"
    assert chunks[0].symbol_scip == symbol
    assert "def alpha" in chunks[0].text


@pytest.mark.integration
def test_chunk_with_scip_infers_document_path_and_language() -> None:
    content = "def alpha():\n    return 1\n"
    symbol = "scip-python pypi pkg 1.0.0 main/alpha()."

    index: Any = _IndexMessage()
    index.metadata.project_root = "file:///repo"

    doc: Any = index.documents.add()
    doc.relative_path = "src/main.py"
    doc.language = "python"

    occ: Any = doc.occurrences.add()
    occ.symbol = symbol
    occ.symbol_roles = 0x1
    occ.range.extend([0, 4, 0, 9])
    occ.enclosing_range.extend([0, 0, 2, 0])

    parsed = ScipParser().parse_bytes(index.SerializeToString())
    chunks = list(chunk_with_scip(content, parsed))

    assert len(chunks) == 1
    assert chunks[0].chunk_type == "scip:def"
    assert chunks[0].symbol_scip == symbol
