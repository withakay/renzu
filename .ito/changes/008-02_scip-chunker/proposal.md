# Proposal: SCIP Chunker

## Why
Use SCIP symbol data for precise semantic chunking with symbol metadata.

## What
Create `app.scip.chunker` module with:
- `ScipChunker` class using parsed SCIP data
- Symbol span extraction (definition ranges)
- Hybrid mode: SCIP definitions + tree-sitter fallback
- symbol_scip field population in chunks

## Impact
- **Enables**: Symbol-aware indexing with SCIP
- **Depends On**: scip-parser
- **PRD Reference**: FR-I2 (SCIP-based chunking)

## Out of Scope
- SCIP parsing
