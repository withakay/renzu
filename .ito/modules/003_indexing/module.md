# Indexing

## Purpose
Code indexing pipeline that transforms source files into vector-searchable chunks. Handles file discovery, parsing, chunking, embedding, and storage in Qdrant.

## Scope
- File walking with include/exclude globs
- Language detection
- Tree-sitter based chunking (baseline)
- Embedding provider abstraction
- Qdrant collection management and upsert
- Indexing job orchestration
- Content hashing and deduplication

## Depends On
- core

## Changes
- [ ] 003-01_qdrant-client
- [ ] 003-02_file-walker
- [ ] 003-03_tree-sitter-chunker
- [ ] 003-04_embedding-provider
- [ ] 003-05_indexing-pipeline
- [ ] 003-06_ollama-provider
