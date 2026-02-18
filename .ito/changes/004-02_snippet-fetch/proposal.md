# Proposal: Snippet Fetch

## Why
Retrieve file spans for citations, providing full context around search results.

## What
Create `app.retrieval.snippet` module with:
- `SnippetService` class
- Fetch by repo_id, path, start_line, end_line
- Path traversal protection
- Line range validation

## Impact
- **Enables**: Full code context for search results
- **PRD Reference**: FR-R3 (Snippet fetch)

## Out of Scope
- Vector search
