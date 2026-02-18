# Proposal: Zoekt Indexer

## Why
Index repositories into Zoekt for lexical search availability.

## What
Create `app.zoekt.indexer` module with:
- `ZoektIndexer` class for triggering index jobs
- Integration with file-walker for file discovery
- Sync with Qdrant indexing pipeline (optional parallel)
- Index status tracking

## Impact
- **Enables**: Zoekt search over indexed repos
- **Depends On**: zoekt-client, file-walker
- **PRD Reference**: Complements FR-I1

## Out of Scope
- Zoekt webserver management
