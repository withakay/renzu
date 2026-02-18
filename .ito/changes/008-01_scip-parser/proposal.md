# Proposal: SCIP Parser

## Why
Parse SCIP indexes for symbol-aware chunking, enabling precise semantic chunks tied to language server data.

## What
Create `app.scip.parser` module with:
- `ScipParser` class for .scip file parsing
- Symbol extraction with roles (definition, reference)
- Occurrence mapping to file locations
- Symbol identifier parsing (scheme, manager, package, descriptors)

## Impact
- **Enables**: SCIP-based chunking
- **PRD Reference**: Section 5.2 (SCIP-based indexing)

## Out of Scope
- SCIP index generation
- Chunking integration
