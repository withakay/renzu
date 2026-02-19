# Tasks for: 011-01_renzu-web-client

## Execution Notes

- **Tool**: OpenCode/Codex
- **Mode**: Sequential
- **Template**: Enhanced waves with verification
- **Tracking**: `ito tasks` CLI

```bash
ito tasks status 011-01_renzu-web-client
ito tasks next 011-01_renzu-web-client
ito tasks start 011-01_renzu-web-client 1.1
ito tasks complete 011-01_renzu-web-client 1.1
```

______________________________________________________________________

## Wave 1

- **Depends On**: None

### Task 1.1: Scaffold frontend foundation

- **Files**: `web-client/*`
- **Dependencies**: None
- **Action**: Initialize Vite React TypeScript app with pnpm and baseline tooling.
- **Verify**: `cd web-client && pnpm install && pnpm build`
- **Done When**: Frontend project builds successfully.
- **Updated At**: 2026-02-19
- **Status**: [ ] pending

### Task 1.2: Add UI stack and project structure

- **Files**: `web-client/package.json`, `web-client/src/**`, `web-client/tailwind*`, `web-client/components.json`
- **Dependencies**: Task 1.1
- **Action**: Configure Tailwind + shadcn, TanStack Query/Router, and app shell structure.
- **Verify**: `cd web-client && pnpm lint && pnpm build`
- **Done When**: App compiles with chosen stack and route skeleton.
- **Updated At**: 2026-02-19
- **Status**: [ ] pending

______________________________________________________________________

## Wave 2

- **Depends On**: Wave 1

### Task 2.1: Implement typed API client and forms

- **Files**: `web-client/src/lib/api.ts`, `web-client/src/features/**`
- **Dependencies**: None
- **Action**: Add request helpers and feature UIs for `/v1/index`, `/v1/search`, `/v1/snippet`, and `/v1/glass/*`.
- **Verify**: `cd web-client && pnpm build`
- **Done When**: Users can submit requests and view structured responses per endpoint.
- **Updated At**: 2026-02-19
- **Status**: [ ] pending

### Task 2.2: Add error/loading/result UX patterns

- **Files**: `web-client/src/components/**`, `web-client/src/features/**`
- **Dependencies**: Task 2.1
- **Action**: Add reusable status panels, JSON viewer, and copy action.
- **Verify**: `cd web-client && pnpm build`
- **Done When**: Every workflow shows consistent pending/success/error behavior.
- **Updated At**: 2026-02-19
- **Status**: [ ] pending

______________________________________________________________________

## Wave 3

- **Depends On**: Wave 2

### Task 3.1: Dockerize static frontend

- **Files**: `web-client/Dockerfile`, `web-client/nginx.conf`, optional compose wiring/docs
- **Dependencies**: None
- **Action**: Add multi-stage build and static hosting image with configurable API base URL.
- **Verify**: `docker build -t renzu-web-client ./web-client`
- **Done When**: Container serves built assets successfully.
- **Updated At**: 2026-02-19
- **Status**: [ ] pending

### Task 3.2: Document runbook

- **Files**: `README.md`, `web-client/README.md`
- **Dependencies**: Task 3.1
- **Action**: Document local dev, env config, and docker usage.
- **Verify**: `make check && make test`
- **Done When**: Docs include startup and verification steps.
- **Updated At**: 2026-02-19
- **Status**: [ ] pending

______________________________________________________________________

## Wave 4 (Checkpoint)

- **Depends On**: Wave 3

### Task 4.1: Review implementation

- **Type**: checkpoint
- **Files**: `web-client/**`, docs, docker artifacts
- **Dependencies**: Task 3.2
- **Action**: Review UX and container flow with maintainers before archive.
- **Done When**: Human approval is provided.
- **Updated At**: 2026-02-19
- **Status**: [ ] pending
