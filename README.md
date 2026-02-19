# Code Context Service

Code RAG with vector search and symbol navigation for AI agents.

## Development

```bash
make install  # Install dependencies
make dev      # Run development server
make check    # Run lint, format, and type checks
make test     # Run unit tests
```

## Infra Services (Docker Compose)

Use the infra-only compose stack to run Qdrant, Glean, and Glass for local development.

Prerequisite: a local checkout of `withakay/glean-docker`.
By default, the compose file expects a symlink at `./.local/glean-docker` (or set `GLEAN_DOCKER_PATH`).

```bash
cp .env.example .env
docker compose -f docker/infra-compose.yml up -d
```

Compatibility alias (same stack, root-level compose file):

```bash
docker compose -f docker-compose.infra.yml up -d
```

Include Ollama only when needed:

```bash
docker compose -f docker/infra-compose.yml --profile ollama up -d
```

Service endpoints:

- Qdrant REST: `http://localhost:6333`
- Qdrant gRPC: `localhost:6334`
- Glean server: `localhost:12345`
- Glass server: `localhost:12346`
- Ollama (profile `ollama`): `http://localhost:11434`

## Full Stack Compose

Run the full stack (infra + code-context service):

```bash
cp .env.example .env
docker compose up -d
```

Run with development override:

```bash
docker compose -f docker-compose.yml -f docker/compose.dev.yml up -d
```

Run with optional static web client (served on `http://localhost:8080`):

```bash
docker compose --profile web up -d --build
```

Run with production override:

```bash
docker compose -f docker-compose.yml -f docker/compose.prod.yml up -d
```

Additional service endpoints for full stack:

- code-context HTTP: `http://localhost:8000`
- code-context MCP port: `localhost:9000`
