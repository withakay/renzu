# PRD: Docker‑first “Talk to My Code” Index + Retrieval Stack (Qdrant + Glean + Tree‑sitter/SCIP + MCP)

**Status:** Draft PRD (PoC → production path)  
**Date:** 2026‑02‑18 (Europe/London)  
**Audience:** Engineering team building the first working stack quickly, then hardening.

---

## 1) Summary

Build a **local, Docker‑first code intelligence stack** that lets an external **agent harness** (OpenCode / Codex CLI / Claude Code) “talk with the code” by calling tools that provide:

1) **Semantic retrieval** of relevant code chunks (vector search in **Qdrant**)  
2) **Precise code navigation** (definitions / references / document symbols) via **Glean + Glass**  
3) **High‑quality chunking** from source using **tree‑sitter** and optionally **SCIP**  
4) **Pluggable embeddings** (remote API or Ollama)

The chat loop, planning, and edits are handled by the agent harness; this project provides the **indexing + retrieval + navigation** substrate.

We expose tool access over:
- **HTTP JSON API** (debugging + integration)
- **MCP server** (Model Context Protocol) so agent harnesses can discover and call tools uniformly.

---

## 2) Problem statement

Developers want to ask questions like:

- “Where is `Foo::bar` implemented and what does it depend on?”
- “What code paths call `validatePayment()`?”
- “Why does this test fail on CI but not locally?”
- “Show me the relevant parts of the codebase for X”

Naive RAG over arbitrary chunks often fails for code because it lacks:
- **symbol-level structure** (defs/refs/call graphs)
- **precise spans** and navigation
- **good chunk boundaries**

This system combines:
- **vector retrieval** (fast “rough relevance”) and  
- **code graph navigation** (exact answers and context expansion)

---

## 3) Goals

### G1 — Docker-first PoC
A `docker compose up` brings up:
- Qdrant (vector DB)
- Glean server + Glass server (symbol server on top of Glean)
- Python “Code Context Service” (index + retrieval + MCP)

### G2 — Index code locally
Given a mounted repo/workspace path:
- parse files
- chunk (tree-sitter baseline; SCIP-enhanced when available)
- embed chunks via configured embedding provider
- upsert to Qdrant

### G3 — Serve retrieval tools for agents
Expose tools to:
- search code semantically
- fetch file spans/snippets
- optionally expand context via Glean/Glass (documentSymbols/findReferences/describe)

### G4 — Interoperate with agent harnesses
Primary integration via **MCP** plus a plain HTTP API.

---

## 4) Non-goals (for PoC)

- Building a full chat UI
- Autonomously editing code (that’s the agent harness job)
- Perfect incremental indexing across huge monorepos (PoC can do full reindex)
- GPU-accelerated vector search (GPU is more valuable for embeddings/inference elsewhere)

---

## 5) Users & primary use cases

### Persona A: “Local agent user”
Runs OpenCode/Codex/Claude Code locally, wants tools to answer questions with correct code context.

**Top user stories**
- As a user, I can ask “what does X do?” and the agent pulls the right files/functions.
- As a user, I can ask “where is X referenced?” and get exact references (not guesses).
- As a user, I can constrain search to a path (`src/`) or language.

### Persona B: “Indexer operator”
Wants to run indexing and keep it up to date.

**Top user stories**
- As an operator, I can index a repo once and query immediately.
- As an operator, I can re-index on demand or on file changes.

---

## 6) Key decisions

### 6.1 Vector DB: Qdrant
- Qdrant runs well in Docker, exposes REST + gRPC, and provides a dashboard UI.

### 6.2 Code graph: Glean + Glass
- Run `glean-server` and `glass-server`; Glass provides higher-level operations like `documentSymbols` and `findReferences`.

### 6.3 Chunking: tree‑sitter baseline + SCIP optional
- Use tree-sitter in Python for fast syntactic/structural chunking.
- Parse `.scip` indexes when present to chunk by symbol-definition spans and attach stable symbol IDs.

### 6.4 Glue: Python 3.14
- Use `python:3.14-slim` for the Code Context Service container.

### 6.5 Agent harness integration: MCP-first
- Expose an MCP server (“code-context”) with a small set of tools.

---

## 7) System architecture overview

```
┌──────────────────────────────┐
│ Agent Harness (OpenCode /     │
│ Codex CLI / Claude Code)      │
│  - chat, planning, edits      │
│  - calls tools via MCP        │
└───────────────┬──────────────┘
                │ MCP (preferred) / HTTP (debug)
┌───────────────▼──────────────┐
│ Code Context Service (Python) │
│  - index pipeline             │
│  - chunking (tree-sitter/SCIP)│
│  - embeddings (API/Ollama)    │
│  - retrieval + filters        │
│  - optional graph expansion   │
└───────┬───────────┬──────────┘
        │           │
        │           └──────────────┐
        │                          │
┌───────▼──────────┐        ┌──────▼──────────┐
│ Qdrant            │        │ Glean + Glass   │
│ - vectors+payload │        │ - defs/refs/etc │
└──────────────────┘        └─────────────────┘
```

---

## 8) Functional requirements

### 8.1 Indexing

**FR‑I1**: Index a workspace directory (bind-mounted) into a named `repo_id`.  
- Inputs: `repo_id`, `root_path`, include/exclude globs, languages, max file size.  
- Outputs: indexing job status + counts (files, chunks, vectors).

**FR‑I2**: Chunking  
- **Tree-sitter chunker (baseline)**
  - extract semantic blocks (functions, classes, methods, modules)
  - fallback to window/line chunking if parse fails
- **SCIP chunker (optional)**
  - if `.scip` exists, prefer symbol-definition spans and attach symbol IDs
  - merge/scoring rules when both tree-sitter and SCIP produce chunks

**FR‑I3**: Embedding  
- Pluggable embedding provider:
  - “remote API”: OpenAI/Anthropic/etc (HTTP)
  - “ollama”: local HTTP call (optional)
- Batch embedding to reduce latency/cost.
- Cache embeddings keyed by `(model, content_hash)` in a local volume.

**FR‑I4**: Store vectors in Qdrant  
- Collection strategy:
  - Option A (PoC): single collection `code_chunks` with `repo_id` payload + filter
  - Option B (later): per-repo collections for isolation and fast deletes

**FR‑I5**: Deletion & refresh  
- Delete by `repo_id` (full wipe) and reindex.
- Incremental indexing is a “v1.1+” enhancement (hash-based diff).

---

### 8.2 Retrieval + context building

**FR‑R1**: Semantic search  
- Input: query string + filters (`repo_id`, `path_prefix`, `language`, `chunk_type`) + `top_k`  
- Behavior: embed query → Qdrant search → return ranked chunks (text + metadata + score)

**FR‑R2**: Return citations  
Each result should include:
- file path
- start_line/end_line (or byte offsets)
- repo_id
- chunk type (tree-sitter vs SCIP)
- (optional) symbol identifiers (SCIP symbol, Glass symbol ID)

**FR‑R3**: Fetch snippet / span  
- Input: `repo_id`, `path`, `start_line`, `end_line`  
- Output: exact slice of file text

**FR‑R4**: Hybrid search (optional)  
- Add lexical scoring later (BM25/FTS-like); PoC can rely on vector search.

---

### 8.3 Code navigation via Glean/Glass (optional but recommended)

**FR‑G1**: list document symbols for a file  
**FR‑G2**: describe symbol (definition span)  
**FR‑G3**: find references for a symbol

**PoC integration approach**
- Call Glass through:
  - a Thrift client (preferred medium-term), or
  - a thin proxy that shells out to `glass-democlient` (fastest PoC).

---

## 9) Non-functional requirements

### Performance
- Query latency target (PoC):
  - total search tool response: < 2s ideal, < 5s acceptable

### Reliability
- Qdrant and Glean DBs persisted in Docker volumes.
- Indexing jobs restartable.

### Security
- Bind to localhost by default (or require token for LAN).
- File read endpoint prevents path traversal (only under workspace root).

### Observability
- Structured logs (JSON)
- `/healthz`, `/readyz`
- Optional `/metrics`

---

## 10) Data model

### 10.1 Qdrant point payload (PoC)

Each chunk is one Qdrant point with payload:

```json
{
  "repo_id": "myrepo",
  "path": "src/foo/bar.rs",
  "language": "rust",
  "chunk_type": "ts:function|ts:class|scip:def|fallback:window",
  "start_line": 120,
  "end_line": 188,
  "start_byte": 4231,
  "end_byte": 6120,
  "symbol_scip": "scip:...optional...",
  "symbol_glass": "glass:...optional...",
  "content_hash": "sha256:...",
  "text": "..."               // PoC ok; later move to blob store
}
```

**Vector:** embedding vector for `text`.

### 10.2 Local blob store (recommended for v1)
Instead of storing full text in Qdrant payload, store it on disk:
- `./data/blobs/<chunk_id>.txt`
and store `blob_path` in Qdrant payload.

---

## 11) Interfaces

### 11.1 HTTP API (debugging + non-MCP clients)

- **POST** `/v1/index` — trigger indexing
- **POST** `/v1/search` — semantic search
- **POST** `/v1/snippet` — fetch file span
- **POST** `/v1/glass/list_symbols` *(optional)*
- **POST** `/v1/glass/find_references` *(optional)*
- **POST** `/v1/glass/describe` *(optional)*

### 11.2 MCP Tools (for OpenCode/Codex/Claude Code)

- `code_search(query, repo_id, path_prefix?, language?, top_k?)`
- `code_snippet(repo_id, path, start_line, end_line)`
- `symbols_in_file(repo_id, path)`  *(Glass)*
- `symbol_references(symbol_id)`    *(Glass)*
- `symbol_definition(symbol_id)`    *(Glass)*

---

## 12) Deployment: Docker Compose (PoC)

> Assumptions:
> - `./services/code_context/` contains the Python service (FastAPI + MCP).
> - `./services/glean/` contains your working Glean Docker build.
> - Repos are bind-mounted from `./repos` into `/workspace`.

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"   # REST + dashboard
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_storage:/qdrant/storage
    healthcheck:
      test: ["CMD", "sh", "-c", "wget -qO- http://localhost:6333/ >/dev/null 2>&1"]
      interval: 10s
      timeout: 3s
      retries: 20

  glean-server:
    build:
      context: ./services/glean
      dockerfile: Dockerfile
    container_name: glean-server
    restart: unless-stopped
    command: ["glean-server", "--db-root", "/data/glean/db", "--schema", "/data/glean/schema/source", "--port", "12345"]
    ports:
      - "12345:12345"
    volumes:
      - glean_db:/data/glean/db
      - ./data/glean/schema:/data/glean/schema:ro
    healthcheck:
      test: ["CMD", "sh", "-c", "nc -z localhost 12345"]
      interval: 10s
      timeout: 3s
      retries: 30

  glass-server:
    build:
      context: ./services/glean
      dockerfile: Dockerfile
    container_name: glass-server
    restart: unless-stopped
    depends_on:
      glean-server:
        condition: service_healthy
    command: ["glass-server", "--service", "glean-server:12345", "--port", "12346"]
    ports:
      - "12346:12346"
    healthcheck:
      test: ["CMD", "sh", "-c", "nc -z localhost 12346"]
      interval: 10s
      timeout: 3s
      retries: 30

  code-context:
    build:
      context: ./services/code_context
      dockerfile: Dockerfile
    container_name: code-context
    restart: unless-stopped
    depends_on:
      qdrant:
        condition: service_healthy
      glass-server:
        condition: service_healthy
    environment:
      QDRANT_URL: "http://qdrant:6333"
      GLASS_HOST: "glass-server"
      GLASS_PORT: "12346"

      WORKSPACE_ROOT: "/workspace"
      BLOB_STORE_DIR: "/data/blobs"

      # Embeddings provider: "api" or "ollama"
      EMBEDDINGS_PROVIDER: "ollama"
      OLLAMA_BASE_URL: "http://host.docker.internal:11434"

      # Model configuration
      EMBEDDINGS_MODEL: "qwen3-embedding"   # example; configurable
      VECTOR_SIZE: "1024"                  # must match model output

      HTTP_PORT: "8000"
      MCP_PORT: "9000"
      LOG_LEVEL: "INFO"
    ports:
      - "8000:8000"   # HTTP API
      - "9000:9000"   # MCP server
    volumes:
      - ./repos:/workspace:ro
      - code_context_data:/data

  # Optional: run Ollama in Docker (CPU-only on macOS Docker Desktop).
  # Enable with: docker compose --profile ollama up
  ollama:
    profiles: ["ollama"]
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  qdrant_storage:
  glean_db:
  code_context_data:
  ollama_data:
```

---

## 13) Implementation notes (Python 3.14)

### Suggested dependencies
- `fastapi`, `uvicorn`
- `qdrant-client`
- `tree-sitter` (+ optional grammar packages)
- `protobuf` (SCIP parsing)
- MCP server library (or implement minimal MCP over HTTP/stdin-stdio)

### Indexer pipeline (high level)
1) Walk files under `WORKSPACE_ROOT`
2) For each file:
   - detect language
   - chunk via tree-sitter; optionally enrich spans from SCIP
   - compute stable IDs + hashes
3) Batch embed chunk texts
4) Upsert points to Qdrant collection
5) Persist blob text if enabled

---

## 14) Milestones

### M0 — Compose boot
- Qdrant + code-context start; health checks pass.

### M1 — Index + search (PoC)
- `/v1/index` and `/v1/search` working end-to-end
- Agent harness can call `code_search` + `code_snippet`

### M2 — Add Glean/Glass tools
- `symbols_in_file`, `symbol_definition`, `symbol_references`
- Optional “expand context” mode uses Glass around top hits

### M3 — SCIP chunking
- Parse `.scip` and use symbol spans
- Store SCIP symbol IDs in payload

### M4 — Hardening
- Incremental indexing
- Better filters, reranking, caching, metrics
- Security review of tool endpoints (path validation, auth)

---

## 15) Risks & mitigations

- **Glean Docker variance:** pin versions, rely on your known-good build.
- **Chunk explosion:** enforce file-size limits and chunk caps.
- **Embedding latency/cost:** batch + cache by content hash.
- **Path traversal:** strict workspace-root enforcement and path canonicalization.
