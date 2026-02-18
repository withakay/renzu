"""FastAPI application entry point."""

from fastapi import FastAPI

from app import __version__

app = FastAPI(
    title="Code Context Service",
    description="Code RAG with vector search and symbol navigation for AI agents",
    version=__version__,
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    """Readiness check endpoint."""
    return {"status": "ready"}
