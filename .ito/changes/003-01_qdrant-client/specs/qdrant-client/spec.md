## ADDED Requirements

### Requirement: Qdrant client wrapper
The application SHALL provide a typed Qdrant client wrapper that manages connections.

#### Scenario: Client connects to configured URL
- **WHEN** the QdrantClient is initialized
- **THEN** it SHALL connect to the URL specified in `QDRANT_URL` config

### Requirement: Collection management
The client SHALL create the `code_chunks` collection with the configured vector size.

#### Scenario: Collection is created on startup
- **WHEN** `ensure_collection()` is called
- **THEN** a collection named `code_chunks` SHALL exist with cosine similarity

### Requirement: Point upsert
The client SHALL support upserting points with the PRD-specified payload schema.

#### Scenario: Point is upserted
- **WHEN** `upsert_points(repo_id, points)` is called
- **THEN** points SHALL be stored with payload containing: repo_id, path, language, chunk_type, start_line, end_line, text, content_hash

### Requirement: Point delete by filter
The client SHALL support deleting points by repo_id filter.

#### Scenario: Points are deleted by repo_id
- **WHEN** `delete_by_repo(repo_id)` is called
- **THEN** all points with matching repo_id SHALL be removed

### Requirement: Health check
The client SHALL provide a health check method for readiness probes.

#### Scenario: Health check returns True when connected
- **WHEN** `health_check()` is called and Qdrant is reachable
- **THEN** it SHALL return `True`
