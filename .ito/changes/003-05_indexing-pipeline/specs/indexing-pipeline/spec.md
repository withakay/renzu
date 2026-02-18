## ADDED Requirements

### Requirement: Index repository endpoint
The pipeline SHALL provide an `index_repo` method.

#### Scenario: Repo is indexed
- **WHEN** `index_repo(repo_id="myrepo", path="/workspace/myrepo")` is called
- **THEN** all matching files SHALL be chunked, embedded, and stored in Qdrant

### Requirement: Progress tracking
The pipeline SHALL log progress during indexing.

#### Scenario: Progress is logged
- **WHEN** indexing is in progress
- **THEN** logs SHALL include file count and chunk count

### Requirement: Per-file error isolation
The pipeline SHALL continue on file errors.

#### Scenario: File error is logged but indexing continues
- **WHEN** a file fails to chunk
- **THEN** the error SHALL be logged and other files SHALL still be processed

### Requirement: Content hash deduplication
The pipeline SHALL skip chunks with unchanged content.

#### Scenario: Unchanged chunks are skipped
- **WHEN** a file is re-indexed with unchanged content
- **THEN** embedding SHALL NOT be called for existing content hashes

### Requirement: Delete before reindex
The pipeline SHALL delete existing points for the repo before indexing.

#### Scenario: Old points are removed
- **WHEN** re-indexing a repo
- **THEN** existing points with matching repo_id SHALL be deleted first
