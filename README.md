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
- code-context MCP (streamable HTTP): `http://localhost:8000/mcp`

### MCP CLI

Generate a typed CLI from the live MCP server:

```bash
make mcp-cli-generate
```

Use the generated CLI:

```bash
uv run --with fastmcp python mcp-cli/renzu-mcp-cli.py --help
uv run --with fastmcp python mcp-cli/renzu-mcp-cli.py list-tools
uv run --with fastmcp python mcp-cli/renzu-mcp-cli.py call-tool code_search --query "mcp http" --repo-id renzu
```

Optional override for remote/local MCP URL:

```bash
RENZU_MCP_URL=http://localhost:8000/mcp \
  uv run --with fastmcp python mcp-cli/renzu-mcp-cli.py list-tools
```

## Getting Started + Troubleshooting

Quick start:

```bash
cp .env.example .env
docker compose --profile web up -d --build
```

Open:

- Web client: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`

Index first (required before search/snippet):

```bash
curl -s -X POST http://localhost:8000/v1/index \
  -H "content-type: application/json" \
  -d '{
    "repo_id":"renzu",
    "path":"/workspace",
    "globs":["src/**/*.py","tests/**/*.py"]
  }'
```

Use your entire code folder:

- Set `WORKSPACE_PATH` in `.env` (example: `WORKSPACE_PATH=/Users/jack/Code`)
- Recreate services: `docker compose down && docker compose up -d --build`
- Keep mount read-only (`:ro`) for safety (already configured)

Common issues:

- **UI shows `Load failed`**: restart API/web services to pick latest CORS support:
  `docker compose up -d --build code-context web-client`
- **Index fails with Qdrant point ID error**: update to latest `main` and rebuild `code-context`
- **Glass shows unavailable or empty data**: ensure `glass-server` is healthy (`docker compose ps`) and re-run `list_symbols`
- **Compose build output crashes in PTY environments**: run with redirected logs:
  `docker compose up -d --build > /tmp/renzu-compose.log 2>&1`
