"""Unit tests for SCIP parser and symbol parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.scip._proto import scip_pb2
from app.scip.parser import ScipParser, parse_symbol_identifier

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.unit
class TestScipSymbolParsing:
    def test_parses_global_symbol_with_descriptors(self) -> None:
        symbol = "scip-python pypi requests 2.31.0 requests/Session#request()."
        parsed = parse_symbol_identifier(symbol)

        assert parsed.scheme == "scip-python"
        assert parsed.manager == "pypi"
        assert parsed.package_name == "requests"
        assert parsed.version == "2.31.0"
        assert [d.kind for d in parsed.descriptors] == ["namespace", "type", "method"]
        assert [d.name for d in parsed.descriptors] == ["requests", "Session", "request"]

    def test_parses_escaped_descriptor_identifier(self) -> None:
        symbol = "scip-ts npm mypkg 1.0.0 `hello world`/Foo#bar()."
        parsed = parse_symbol_identifier(symbol)
        assert parsed.descriptors[0].name == "hello world"
        assert parsed.descriptors[0].kind == "namespace"

    def test_parses_local_symbol(self) -> None:
        parsed = parse_symbol_identifier("local abc123")
        assert parsed.is_local
        assert parsed.local_id == "abc123"


@pytest.mark.unit
class TestScipParser:
    def test_parses_index_file_and_extracts_roles(self, tmp_path: Path) -> None:
        Index = getattr(scip_pb2, "Index")  # noqa: B009
        Document = getattr(scip_pb2, "Document")  # noqa: B009
        Occurrence = getattr(scip_pb2, "Occurrence")  # noqa: B009

        index = Index()
        index.metadata.project_root = "file:///repo"

        doc = Document()
        doc.relative_path = "src/main.py"
        doc.language = "python"

        def_occ = Occurrence()
        def_occ.symbol = "scip-python pypi pkg 1.0.0 main/Greeter#hello()."
        def_occ.symbol_roles = 0x1
        def_occ.range.extend([0, 0, 0, 6])
        doc.occurrences.append(def_occ)

        ref_occ = Occurrence()
        ref_occ.symbol = def_occ.symbol
        ref_occ.symbol_roles = 0x0
        ref_occ.range.extend([1, 0, 3])
        doc.occurrences.append(ref_occ)

        index.documents.append(doc)

        path = tmp_path / "index.scip"
        path.write_bytes(index.SerializeToString())

        parsed = ScipParser().parse_file(path)

        assert parsed.metadata_project_root == "file:///repo"
        assert len(parsed.documents) == 1
        occurrences = list(parsed.iter_occurrences())
        assert len(occurrences) == 2
        assert "definition" in occurrences[0].roles
        assert "reference" in occurrences[1].roles
        assert occurrences[0].range.start_line == 0
        assert occurrences[1].range.end_line == 1
