<!-- ITO:START -->
## Context

Renzu currently ships a Python API and MCP tooling, but user interaction is mostly CLI/curl-driven. A static web app improves accessibility for developers and reviewers while keeping deployment lightweight. The frontend must call existing `/v1/*` endpoints, handle mixed success/error payloads, and run both locally (`pnpm dev`) and in Docker.

## Goals / Non-Goals

**Goals:**

- Build a TypeScript SPA in `web-client/` using Vite + pnpm.
- Use TanStack Query for request state and caching.
- Use TanStack Router for route organization.
- Use shadcn/ui primitives for consistent interaction patterns.
- Provide dedicated pages/panels for index/search/snippet/glass operations.
- Ship Docker packaging for static hosting.

**Non-Goals:**

- Replace backend authentication/authorization model.
- Add server-side rendering or Next.js migration.
- Redesign backend APIs in this change.

## Decisions

- **Vite SPA + React + TypeScript**: simplest static deployment and aligns with requested stack.
- **TanStack Query over ad-hoc hooks**: standard async lifecycle and retry/error control for API-heavy UI.
- **TanStack Router over single-page tabs**: preserves room for growth and deep-linking for specific workflows.
- **shadcn/ui on Tailwind**: fast, consistent UI primitives while still allowing custom design language.
- **Typed API layer + Zod parsers**: runtime guardrails for backend payload drift and safer UI rendering.
- **Nginx static container**: small and predictable production serving model.

## Risks / Trade-offs

- **[Risk] Endpoint payload drift** -> Mitigation: centralize Zod schemas and tolerant display fallback for unknown fields.
- **[Risk] CORS mismatch in mixed deployments** -> Mitigation: document API base URL config and reverse-proxy pattern.
- **[Risk] UI complexity creep** -> Mitigation: keep V1 scope to direct API workflows and defer advanced visualization.

## Migration Plan

1. Scaffold `web-client/` and install requested dependencies.
2. Implement core layout, API client, and feature routes.
3. Add Dockerfile + optional compose integration/docs.
4. Validate frontend build/lint and end-to-end calls against local Renzu API.

Rollback: remove `web-client/` and related Docker/docs additions if deployment issues occur.

## Open Questions

- Should the web client be served on a dedicated port in `docker-compose.yml` by default or as an optional profile?
- Should `repo_id` default to `renzu` in forms, or remain explicitly required each request?
<!-- ITO:END -->
