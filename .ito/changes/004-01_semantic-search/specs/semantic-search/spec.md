## ADDED Requirements

### Requirement: Semantic search with filters
The search service SHALL support vector similarity search with multiple filters.

#### Scenario: Search with repo_id filter
- **WHEN** `search(query, repo_id="myrepo")` is called
- **THEN** only results from that repo SHALL be returned

#### Scenario: Search with path_prefix filter
- **WHEN** `search(query, path_prefix="src/app")` is called
- **THEN** only results with paths starting with that prefix SHALL be returned

#### Scenario: Search with language filter
- **WHEN** `search(query, language="python")` is called
- **THEN** only Python files SHALL be returned

### Requirement: Top-k configurable results
The search service SHALL support configurable result count.

#### Scenario: Top-k is respected
- **WHEN** `search(query, top_k=5)` is called
- **THEN** at most 5 results SHALL be returned

### Requirement: Citation formatting
Results SHALL include citation metadata per PRD spec.

#### Scenario: Citation includes required fields
- **WHEN** a search result is returned
- **THEN** it SHALL include: repo_id, path, start_line, end_line, chunk_type, score
