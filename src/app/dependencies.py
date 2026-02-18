"""Dependency injection and health checks."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import get_settings
from app.indexing.qdrant import get_qdrant_client


@dataclass
class HealthStatus:
    """Health check result."""

    healthy: bool
    name: str
    detail: str | None = None


async def check_qdrant() -> HealthStatus:
    """Check if Qdrant is reachable."""
    _ = get_settings()
    qdrant_client = get_qdrant_client()
    try:
        is_healthy = await qdrant_client.health_check()
        if is_healthy:
            return HealthStatus(healthy=True, name="qdrant")

        return HealthStatus(healthy=False, name="qdrant", detail="Connection refused")
    except httpx.ConnectError:
        return HealthStatus(healthy=False, name="qdrant", detail="Connection refused")
    except httpx.TimeoutException:
        return HealthStatus(healthy=False, name="qdrant", detail="Connection timed out")
    except Exception as e:
        return HealthStatus(healthy=False, name="qdrant", detail=str(e))


async def check_all_dependencies() -> tuple[bool, list[HealthStatus]]:
    """Check all dependencies and return overall health status."""
    results = await check_qdrant()
    all_healthy = results.healthy
    return all_healthy, [results]
