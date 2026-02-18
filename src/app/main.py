"""FastAPI application entry point."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Response

from app import __version__
from app.api.routes import register_routes
from app.config import get_settings
from app.dependencies import check_all_dependencies
from app.logging_config import setup_logging
from app.middleware import CorrelationIdMiddleware, RequestLoggingMiddleware

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(
    title="Code Context Service",
    description="Code RAG with vector search and symbol navigation for AI agents",
    version=__version__,
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

register_routes(app)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Liveness probe - always returns 200 if the process is alive."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(response: Response) -> dict[str, Any]:
    """Readiness probe - returns 200 if dependencies are reachable, 503 otherwise."""
    all_healthy, results = await check_all_dependencies()
    if not all_healthy:
        response.status_code = 503
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": {r.name: {"healthy": r.healthy, "detail": r.detail} for r in results},
    }
