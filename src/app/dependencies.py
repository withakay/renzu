"""Dependency injection and health checks."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import get_settings


@dataclass
class HealthStatus:
    """Health check result."""

    healthy: bool
    name: str
    detail: str | None = None


async def check_qdrant() -> HealthStatus:
    """Check if Qdrant is reachable."""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.qdrant_url}/")
            if response.status_code == 200:
                return HealthStatus(healthy=True, name="qdrant")
            return HealthStatus(
                healthy=False,
                name="qdrant",
                detail=f"Unexpected status: {response.status_code}",
            )
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
