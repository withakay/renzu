## ADDED Requirements

### Requirement: Repository indexing
The indexer SHALL index repositories into Zoekt.

#### Scenario: Repo is indexed
- **WHEN** `index_repo(repo_id="myrepo", path="/workspace/myrepo")` is called
- **THEN** the repo SHALL be indexed by Zoekt webserver

### Requirement: Incremental indexing
The indexer SHALL support incremental updates.

#### Scenario: Only changed files are reindexed
- **WHEN** a repo is reindexed
- **THEN** Zoekt SHALL only process changed files

### Requirement: Index status tracking
The indexer SHALL track indexing status.

#### Scenario: Status is queryable
- **WHEN** `index_status(repo_id)` is called
- **THEN** current index state (pending, complete, error) SHALL be returned

### Requirement: Parallel with Qdrant
The indexer SHALL support parallel indexing with Qdrant.

#### Scenario: Both indexes update together
- **WHEN** `index_repo` is called with `parallel=True`
- **THEN** both Zoekt and Qdrant SHALL be updated

### Requirement: Feature flag control
The indexer SHALL respect feature flag.

#### Scenario: Disabled indexer is no-op
- **WHEN** `ZOEKT_ENABLED=false`
- **THEN** indexing calls SHALL be no-ops
