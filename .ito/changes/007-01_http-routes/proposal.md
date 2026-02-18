# Proposal: HTTP Routes

## Why
Expose indexing, retrieval, and Glass capabilities via REST API for debugging and direct access.

## What
Create `app.api.routes` module with:
- POST `/v1/index` - trigger indexing job
- POST `/v1/search` - semantic search
- POST `/v1/snippet` - fetch file span
- POST `/v1/glass/list_symbols` - symbols in file
- POST `/v1/glass/find_references` - symbol references
- POST `/v1/glass/describe` - symbol details

## Impact
- **Enables**: HTTP access to all capabilities
- **Depends On**: indexing-pipeline, semantic-search, snippet-fetch, glass-tools
- **PRD Reference**: Section 9 (HTTP Endpoints)

## Out of Scope
- MCP server
