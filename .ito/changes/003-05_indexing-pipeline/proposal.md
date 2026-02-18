# Proposal: Indexing Pipeline

## Why
Orchestrate the full indexing workflow: discover files → chunk → embed → store in Qdrant.

## What
Create `app.indexing.pipeline` module with:
- `IndexingPipeline` class
- `index_repo(repo_id, path, globs, languages)` async method
- Progress tracking and logging
- Error handling with per-file isolation
- Content hash deduplication

## Impact
- **Enables**: Complete indexing workflow
- **Depends On**: file-walker, tree-sitter-chunker, embedding-provider, qdrant-client
- **PRD Reference**: FR-I1 to FR-I5

## Out of Scope
- HTTP endpoint trigger
- MCP tool
