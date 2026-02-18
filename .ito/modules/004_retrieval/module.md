# Retrieval

## Purpose
Semantic code search and snippet retrieval. Enables agents to find relevant code chunks via vector similarity and fetch exact file spans.

## Scope
- Semantic search with filters (repo_id, path_prefix, language, chunk_type)
- Result ranking and scoring
- Snippet/span fetching from files
- Citation metadata generation

## Depends On
- core
- indexing (needs Qdrant collection structure)

## Changes
- [ ] 004-01_semantic-search
- [ ] 004-02_snippet-fetch
