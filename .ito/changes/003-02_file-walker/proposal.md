# Proposal: File Walker

## Why
Discover source files to index with configurable include/exclude patterns and language detection.

## What
Create `app.indexing.walker` module with:
- `FileWalker` class with glob-based filtering
- Language detection from file extension
- File metadata extraction (size, mtime)
- Generator-based iteration for memory efficiency

## Impact
- **Enables**: Indexing pipeline file discovery
- **PRD Reference**: FR-I1 (Index workspace to repo_id)

## Out of Scope
- File content reading
- Chunking
