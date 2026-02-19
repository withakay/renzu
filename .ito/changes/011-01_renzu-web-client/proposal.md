<!-- ITO:START -->
## Why

Renzu currently exposes strong HTTP APIs for indexing, search, snippet retrieval, and symbol navigation, but there is no first-party UI for everyday use. A static web client will make these capabilities easier to explore, demo, and operate without hand-writing curl requests.

## What Changes

- Add a TypeScript SPA in `web-client/` using pnpm, TanStack Query, TanStack Router, and shadcn/ui components.
- Provide interactive screens for API health, indexing, semantic search, snippet fetch, and Glass symbol workflows.
- Add a shared API client layer with runtime validation, request/response typing, loading/error handling, and copyable JSON output.
- Add production build + containerization for the web client (static assets served by Nginx) with configurable API base URL.
- Add local run/build documentation and compose guidance for using the UI with the existing Renzu stack.

## Capabilities

### New Capabilities

- `web-client-ui`: Browser-based workflow for index/search/snippet/glass operations against Renzu APIs.
- `web-client-deploy`: Static build and Docker packaging path for local and containerized deployment.

### Modified Capabilities

- None.

## Impact

- New frontend project subtree (`web-client/`) with TypeScript, TanStack, shadcn, and build tooling.
- New Docker artifacts for static hosting and optional compose integration for local full-stack usage.
- Documentation updates for setup and usage.
<!-- ITO:END -->
