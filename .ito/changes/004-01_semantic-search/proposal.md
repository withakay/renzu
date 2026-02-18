# Proposal: Semantic Search

## Why
Enable vector similarity search over indexed code chunks with filtering support.

## What
Create `app.retrieval.search` module with:
- `SearchService` class using Qdrant search API
- Filter support: repo_id, path_prefix, language, chunk_type
- Top-k configurable results
- Citation formatting per PRD spec

## Impact
- **Enables**: Code search for MCP and HTTP API
- **Depends On**: qdrant-client, embedding-provider
- **PRD Reference**: FR-R1 (Semantic search), FR-R2 (Citations)

## Out of Scope
- Snippet fetching
- Glass integration
