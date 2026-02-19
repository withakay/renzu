# Renzu Web Client

Static frontend for the Renzu APIs.

## Stack

- TypeScript + React (Vite)
- TanStack Query
- TanStack Router
- shadcn-style UI primitives
- pnpm

## Local Development

```bash
pnpm install
pnpm dev
```

By default, the app calls `http://localhost:8000`.

To override backend URL:

```bash
VITE_API_BASE_URL=http://localhost:8000 pnpm dev
```

## Build

```bash
pnpm lint
pnpm build
```

## Docker

```bash
docker build -t renzu-web-client ./web-client
docker run --rm -p 8080:80 renzu-web-client
```

To point the built app at a different API base URL:

```bash
docker build \
  --build-arg VITE_API_BASE_URL=http://host.docker.internal:8000 \
  -t renzu-web-client ./web-client
```
