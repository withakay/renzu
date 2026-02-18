## ADDED Requirements

### Requirement: Embedding provider protocol
The application SHALL define an `EmbeddingProvider` protocol with an `embed` method.

#### Scenario: Protocol has embed method
- **WHEN** a class implements `EmbeddingProvider`
- **THEN** it SHALL provide `async embed(texts: list[str]) -> list[list[float]]`

### Requirement: OpenAI embedder implementation
The application SHALL provide an OpenAI-based embedder.

#### Scenario: OpenAI embedder produces vectors
- **WHEN** `OpenAIEmbedder(model="text-embedding-3-small").embed(["hello"])` is called
- **THEN** it SHALL return a list of vectors with correct dimensionality

### Requirement: Content hash caching
The application SHALL provide a caching wrapper for embedders.

#### Scenario: Cache avoids duplicate API calls
- **WHEN** the same text is embedded twice
- **THEN** the API SHALL only be called once

### Requirement: Batch embedding
The embedder SHALL support batching multiple texts.

#### Scenario: Multiple texts are embedded together
- **WHEN** `embed([text1, text2, text3])` is called
- **THEN** a single API call SHALL be made with all texts
