# Design: Glass Client (HTTP)

## Context

This change adds a small HTTP wrapper around a Glass-compatible service so the
application can perform symbol-level navigation (document symbols, describe a
symbol, and find references).

## Goals

- Provide a typed, async HTTP client (`app.glass.client.GlassClient`).
- Make the service URL configurable via `GLASS_URL` (`Settings.glass_url`).
- Degrade gracefully when Glass is not configured or is unavailable.

## Non-Goals

- Defining MCP tools (tracked as `005-02_glass-tools`).
- Implementing a Glass server.

## Decisions

- **HTTP client**: `httpx.AsyncClient` for async I/O and good test support.
- **Endpoint namespace**: `/v1/glass/*` (list, describe, find_references).
- **Error handling**: default `graceful=True` returns empty results on
  unavailability; `graceful=False` raises typed exceptions.
- **Models**: lightweight Pydantic models with `extra="ignore"` for forward
  compatibility.

## Risks / Trade-offs

- Glass response shapes may vary; the client is defensive and treats unknown
  shapes as empty (when graceful).
