# Proposal: Tree-Sitter Chunker

## Why
Split source files into semantic chunks for embedding. Tree-sitter provides language-aware parsing.

## What
Create `app.indexing.chunker` module with:
- `TreeSitterChunker` class with language support
- Semantic block extraction (functions, classes, methods)
- Fallback to window/line chunking for unsupported languages
- Chunk metadata: chunk_type, start_line, end_line, symbol hints

## Impact
- **Enables**: Semantic chunking for indexing
- **PRD Reference**: FR-I2 (Chunking via tree-sitter)

## Out of Scope
- SCIP-based chunking (handled in scip module)
- Embedding
