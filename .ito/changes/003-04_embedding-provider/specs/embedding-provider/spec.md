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

### Requirement: Configurable batching with preserved ordering
The application SHALL support splitting embedding calls into multiple requests when the input list is larger than a configured maximum batch size.

#### Scenario: Large input list is chunked into batches
- **WHEN** `OpenAIEmbedder(max_batch_size=2).embed([t1, t2, t3])` is called
- **THEN** the provider SHALL make 2 API requests and return vectors in `[t1, t2, t3]` order

### Requirement: Rate limiting between batch requests
The application SHALL support rate limiting between embedding API requests when configured.

#### Scenario: Rate limiter is invoked per request
- **WHEN** an embedder is configured with a rate limiter and a request requires multiple batches
- **THEN** the rate limiter SHALL be awaited once per batch request

### Requirement: Embedding dimension configuration
The application SHALL allow configuring the embedding vector size, and it MUST validate that provider responses match the expected dimensionality.

#### Scenario: Explicit dimension is enforced
- **WHEN** `OpenAIEmbedder(vector_size=3).embed(["hello"])` receives a 2-element vector
- **THEN** it SHALL raise an error indicating the dimensionality mismatch

### Requirement: Embedding provider factory
The application SHALL provide a factory for constructing the configured embedding provider and applying the configured cache wrapper.

#### Scenario: Factory returns cached OpenAI provider
- **WHEN** settings specify `embedding_provider="openai"` and caching enabled
- **THEN** `get_embedder()` SHALL return a provider that wraps an OpenAI implementation with a cache layer
