## ADDED Requirements

### Requirement: Ollama embedder implementation
The application SHALL provide an Ollama-based embedder.

#### Scenario: Ollama embedder produces vectors
- **WHEN** `OllamaEmbedder(model="nomic-embed-text").embed(["hello"])` is called
- **THEN** it SHALL return a list of vectors via Ollama API

### Requirement: Configurable Ollama URL
The Ollama embedder SHALL use configurable base URL.

#### Scenario: Custom URL is used
- **WHEN** `OLLAMA_URL=http://custom:11434` is set
- **THEN** the embedder SHALL connect to that URL

### Requirement: Connection error handling
The Ollama embedder SHALL handle connection errors gracefully.

#### Scenario: Connection error raises descriptive exception
- **WHEN** Ollama is not reachable
- **THEN** a descriptive error SHALL be raised indicating the connection failure

### Requirement: Batch support
The Ollama embedder SHALL support batch embedding.

#### Scenario: Multiple texts are embedded
- **WHEN** `embed([text1, text2])` is called
- **THEN** all texts SHALL be embedded in the request
