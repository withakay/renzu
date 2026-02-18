# Zoekt Integration (Optional)

## Purpose
Fast trigram-based lexical search complement to Qdrant semantic search. Provides regex/pattern matching, substring search, and symbol-aware ranking via ctags.

## Scope
- Zoekt webserver client (JSON/gRPC API)
- Repository indexing pipeline
- MCP tools for lexical search

## Depends On
- core

## Status
Optional - enabled via feature flag when Zoekt service is available.

## Changes
- [ ] 010-01_zoekt-client
- [ ] 010-02_zoekt-indexer
- [ ] 010-03_zoekt-tools
