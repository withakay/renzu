"""HTTP route handlers for the FastAPI application.

These endpoints mirror core capabilities for debugging and direct access.
"""

from __future__ import annotations

import hashlib
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import httpx
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.glass.service import (
    GlassResponse,
    SymbolDefinitionRequest,
    SymbolReferencesRequest,
    SymbolsInFileRequest,
    get_glass_service,
)
from app.indexing.chunker import TreeSitterChunker
from app.indexing.qdrant import ChunkPayload, ChunkPoint, QdrantClient, get_qdrant_client
from app.indexing.walker import FileWalker


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ApiError(Exception):
    status_code: int
    error: str
    detail: str | None = None


def _api_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, ApiError):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="internal_error", detail=str(exc)).model_dump(),
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.error, detail=exc.detail).model_dump(),
    )


router = APIRouter(prefix="/v1")


class IndexRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo_id: str = Field(min_length=1)
    path: str = Field(min_length=1, description="Local filesystem path to repository root")
    globs: list[str] = Field(default_factory=lambda: ["**/*"])


class IndexResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    job_id: str
    repo_id: str
    root_path: str
    indexed_files: int
    indexed_chunks: int


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    repo_id: str = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    path_prefix: str | None = None
    language: str | None = None


class SearchHit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    start_line: int
    end_line: int
    score: float
    text: str


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    repo_id: str
    query: str
    hits: list[SearchHit]


class SnippetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo_id: str = Field(min_length=1)
    path: str = Field(min_length=1, description="Repository-relative path")
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)


class SnippetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    repo_id: str
    path: str
    start_line: int
    end_line: int
    content: str


class GlassPassthroughResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    available: bool
    formatted: str
    data: Any | None = None
    error: str | None = None


_repo_roots: dict[str, Path] = {}


def clear_repo_roots() -> None:
    """Clear in-memory repo root mappings.

    Intended for tests.
    """

    _repo_roots.clear()


def _pseudo_embedding(text: str, *, dim: int) -> list[float]:
    """Deterministic embedding for development/debugging.

    This intentionally avoids external embedding dependencies.
    """

    digest = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], "big", signed=False)
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(dim)]


def _resolve_repo_root(repo_id: str) -> Path:
    root = _repo_roots.get(repo_id)
    if root is None:
        raise ApiError(
            status_code=404,
            error="unknown_repo",
            detail=f"Unknown repo_id: {repo_id}. Call POST /v1/index first.",
        )
    return root


def _safe_join(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ApiError(
            status_code=400, error="invalid_path", detail="Path escapes repo root"
        ) from exc
    return candidate


async def _index_repo(
    *,
    qdrant: QdrantClient,
    repo_id: str,
    root: Path,
    globs: list[str],
) -> tuple[int, int]:
    await qdrant.ensure_collection()
    await qdrant.delete_by_repo(repo_id)

    walker = FileWalker(include=globs, exclude=[".git/**", ".venv/**", "**/__pycache__/**"])
    chunker = TreeSitterChunker()

    indexed_files = 0
    indexed_chunks = 0
    buffer: list[ChunkPoint] = []

    async def flush() -> None:
        nonlocal indexed_chunks
        if not buffer:
            return
        await qdrant.upsert_points(repo_id, buffer)
        indexed_chunks += len(buffer)
        buffer.clear()

    for info in walker.walk(root):
        language = info.language or "text"
        try:
            content = info.path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError:
            continue

        chunks = list(chunker.chunk(content, language=language))
        if not chunks:
            continue

        indexed_files += 1
        for chunk in chunks:
            payload = ChunkPayload(
                repo_id=repo_id,
                path=info.relative_path,
                language=language,
                chunk_type=chunk.chunk_type,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                text=chunk.text,
                content_hash=chunk.content_hash,
            )
            point_id = (
                f"{info.relative_path}:{chunk.start_line}:{chunk.end_line}:{chunk.content_hash}"
            )
            vector = _pseudo_embedding(chunk.text, dim=qdrant.vector_size)
            buffer.append(ChunkPoint(id=point_id, vector=vector, payload=payload))
            if len(buffer) >= 64:
                await flush()

    await flush()
    return indexed_files, indexed_chunks


@router.post(
    "/index",
    response_model=IndexResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def post_index(request: IndexRequest) -> IndexResponse:
    root = Path(request.path).expanduser()
    if not root.exists() or not root.is_dir():
        raise ApiError(
            status_code=400, error="invalid_root", detail="path must be an existing directory"
        )

    qdrant = get_qdrant_client()
    job_id = str(uuid.uuid4())

    try:
        indexed_files, indexed_chunks = await _index_repo(
            qdrant=qdrant,
            repo_id=request.repo_id,
            root=root,
            globs=request.globs,
        )
    except httpx.HTTPError as exc:
        raise ApiError(status_code=503, error="dependency_unavailable", detail=str(exc)) from exc
    except Exception as exc:
        raise ApiError(status_code=500, error="index_failed", detail=str(exc)) from exc

    _repo_roots[request.repo_id] = root.resolve()
    return IndexResponse(
        ok=True,
        job_id=job_id,
        repo_id=request.repo_id,
        root_path=str(root.resolve()),
        indexed_files=indexed_files,
        indexed_chunks=indexed_chunks,
    )


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def post_search(request: SearchRequest) -> SearchResponse:
    _ = _resolve_repo_root(request.repo_id)
    qdrant = get_qdrant_client()
    query_vector = _pseudo_embedding(request.query, dim=qdrant.vector_size)

    try:
        results = await qdrant.search(
            query_vector,
            limit=request.top_k,
            repo_id=request.repo_id,
            path_prefix=request.path_prefix,
            language=request.language,
        )
    except httpx.HTTPError as exc:
        raise ApiError(status_code=503, error="dependency_unavailable", detail=str(exc)) from exc
    except Exception as exc:
        raise ApiError(status_code=500, error="search_failed", detail=str(exc)) from exc

    hits: list[SearchHit] = []
    for point in results:
        payload = getattr(point, "payload", None)
        if not isinstance(payload, dict):
            continue
        payload_dict = cast("dict[str, Any]", payload)
        try:
            hits.append(
                SearchHit(
                    path=str(payload_dict.get("path") or ""),
                    start_line=int(payload_dict.get("start_line") or 1),
                    end_line=int(payload_dict.get("end_line") or 1),
                    score=float(getattr(point, "score", 0.0)),
                    text=str(payload_dict.get("text") or ""),
                )
            )
        except Exception:
            continue

    return SearchResponse(ok=True, repo_id=request.repo_id, query=request.query, hits=hits)


@router.post(
    "/snippet",
    response_model=SnippetResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def post_snippet(request: SnippetRequest) -> SnippetResponse:
    if request.end_line < request.start_line:
        raise ApiError(
            status_code=400, error="invalid_range", detail="end_line must be >= start_line"
        )

    root = _resolve_repo_root(request.repo_id)
    file_path = _safe_join(root, request.path)
    if not file_path.exists() or not file_path.is_file():
        raise ApiError(status_code=404, error="not_found", detail="File not found")

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise ApiError(
            status_code=400, error="binary_file", detail="File is not UTF-8 text"
        ) from exc
    except OSError as exc:
        raise ApiError(status_code=500, error="read_failed", detail=str(exc)) from exc

    start_index = max(request.start_line - 1, 0)
    end_index = min(request.end_line, len(lines))
    content = "".join(lines[start_index:end_index])
    return SnippetResponse(
        ok=True,
        repo_id=request.repo_id,
        path=request.path,
        start_line=request.start_line,
        end_line=request.end_line,
        content=content,
    )


def _glass_response_to_passthrough(response: GlassResponse) -> GlassPassthroughResponse:
    return GlassPassthroughResponse(
        ok=response.ok,
        available=response.available,
        formatted=response.formatted,
        data=response.data,
        error=response.error,
    )


@router.post(
    "/glass/list_symbols",
    response_model=GlassPassthroughResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def post_glass_list_symbols(request: SymbolsInFileRequest) -> GlassPassthroughResponse:
    service = get_glass_service()
    try:
        response = await service.symbols_in_file(request)
    except Exception as exc:
        raise ApiError(status_code=500, error="glass_failed", detail=str(exc)) from exc
    return _glass_response_to_passthrough(response)


@router.post(
    "/glass/find_references",
    response_model=GlassPassthroughResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def post_glass_find_references(request: SymbolReferencesRequest) -> GlassPassthroughResponse:
    service = get_glass_service()
    try:
        response = await service.symbol_references(request)
    except Exception as exc:
        raise ApiError(status_code=500, error="glass_failed", detail=str(exc)) from exc
    return _glass_response_to_passthrough(response)


@router.post(
    "/glass/describe",
    response_model=GlassPassthroughResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def post_glass_describe(request: SymbolDefinitionRequest) -> GlassPassthroughResponse:
    service = get_glass_service()
    try:
        response = await service.symbol_definition(request)
    except Exception as exc:
        raise ApiError(status_code=500, error="glass_failed", detail=str(exc)) from exc
    return _glass_response_to_passthrough(response)


def register_routes(app: FastAPI) -> None:
    """Register API routes and exception handlers on an app."""

    app.add_exception_handler(ApiError, _api_error_handler)
    app.include_router(router)
