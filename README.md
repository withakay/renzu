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
