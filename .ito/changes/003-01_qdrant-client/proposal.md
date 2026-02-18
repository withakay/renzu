# Proposal: Qdrant Client

## Why
Centralize Qdrant operations behind a typed client interface. Needed before indexing can store vectors.

## What
Create `app.indexing.qdrant` module with:
- `QdrantClient` wrapper with connection management
- Collection creation with configured schema
- Point upsert operations
- Point delete by filter
- Health check integration for /readyz

## Impact
- **Enables**: Vector storage for indexing pipeline
- **Depends On**: config-and-health (QDRANT_URL config)
- **PRD Reference**: FR-I4 (Store in Qdrant)

## Out of Scope
- Search operations (handled in retrieval module)
- Embedding generation
