"""SCIP index parsing utilities."""

from __future__ import annotations

from app.scip.chunker import ScipChunker
from app.scip.parser import (
    ScipDocument,
    ScipDocumentOccurrence,
    ScipIndex,
    ScipParser,
    ScipRange,
    SymbolDescriptor,
    SymbolIdentifier,
    parse_symbol_identifier,
)

__all__ = [
    "ScipChunker",
    "ScipDocument",
    "ScipDocumentOccurrence",
    "ScipIndex",
    "ScipParser",
    "ScipRange",
    "SymbolDescriptor",
    "SymbolIdentifier",
    "parse_symbol_identifier",
]
