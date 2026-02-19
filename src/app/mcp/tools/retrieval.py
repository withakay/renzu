"""MCP retrieval tools for code search and snippet fetch."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, cast

from app.retrieval.search import get_search_service
from app.retrieval.snippet import Snippet, get_snippet_service
from app.zoekt.client import ZoektFileMatch, ZoektLineMatch, get_zoekt_client

MAX_TOP_K = 100


class SearchToolService(Protocol):
    async def search(
        self,
        query: str,
        *,
        top_k: int | None = None,
        repo_id: str | None = None,
        path_prefix: str | None = None,
        language: str | None = None,
    ) -> list[Any]: ...


class SnippetToolService(Protocol):
    def fetch_snippet(
        self,
        repo_id: str,
        path: str,
        *,
        start_line: int,
        end_line: int,
        context_lines: int = 0,
    ) -> Snippet: ...


class ZoektToolClient(Protocol):
    async def search(
        self,
        query: str,
        *,
        num: int = 20,
        file_pattern: str | None = None,
    ) -> list[ZoektFileMatch]: ...


def _normalize_required(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _format_search_citation(*, repo_id: str, path: str, start_line: int, end_line: int) -> str:
    return f"{repo_id}:{path}:{start_line}-{end_line}"


def _format_snippet_citation(*, repo_id: str, path: str, start_line: int, end_line: int) -> str:
    return f"{repo_id}:{path}:{start_line}-{end_line}"


def _snippet_response(*, repo_id: str, path: str, snippet: Snippet) -> dict[str, Any]:
    return {
        "repo_id": repo_id,
        "path": path,
        "start_line": snippet.start_line,
        "end_line": snippet.end_line,
        "content": snippet.content,
        "citation": _format_snippet_citation(
            repo_id=repo_id,
            path=path,
            start_line=snippet.start_line,
            end_line=snippet.end_line,
        ),
    }


def _lexical_result(
    *,
    repo_id: str,
    path: str,
    score: float,
    line_match: ZoektLineMatch,
) -> dict[str, Any]:
    citation = _format_search_citation(
        repo_id=repo_id,
        path=path,
        start_line=line_match.line_number,
        end_line=line_match.line_number,
    )
    return {
        "text": line_match.line,
        "match_text": line_match.line,
        "path": path,
        "start_line": line_match.line_number,
        "end_line": line_match.line_number,
        "score": score,
        "language": None,
        "chunk_type": "lexical",
        "citation": citation,
    }


def _register_tool(
    *, server: Any, name: str, description: str, handler: Callable[..., Any]
) -> None:
    tool = getattr(server, "tool", None)
    if not callable(tool):
        raise RuntimeError("Provided server does not expose a tool registration API")
    decorator_factory = cast(
        Callable[..., Callable[[Callable[..., Any]], Callable[..., Any]]], tool
    )
    decorator = decorator_factory(name=name, description=description)
    decorator(handler)


def register_retrieval_tools(
    *,
    server: Any,
    search_service: SearchToolService | None = None,
    snippet_service: SnippetToolService | None = None,
    zoekt_client: ZoektToolClient | None = None,
    search_service_getter: Callable[[], SearchToolService] = get_search_service,
    snippet_service_getter: Callable[[], SnippetToolService] = get_snippet_service,
    zoekt_client_getter: Callable[[], ZoektToolClient | None] = get_zoekt_client,
) -> None:
    """Register retrieval tools on the provided MCP server."""

    async def code_search(
        query: str,
        repo_id: str,
        path_prefix: str | None = None,
        language: str | None = None,
        top_k: int = 10,
    ) -> dict[str, Any]:
        normalized_query = _normalize_required(query, field_name="query")
        normalized_repo_id = _normalize_required(repo_id, field_name="repo_id")
        normalized_path_prefix = _normalize_optional(path_prefix)
        normalized_language = _normalize_optional(language)
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        if top_k > MAX_TOP_K:
            raise ValueError(f"top_k must be <= {MAX_TOP_K}")

        resolved_search_service = search_service or search_service_getter()
        search_results = await resolved_search_service.search(
            normalized_query,
            top_k=top_k,
            repo_id=normalized_repo_id,
            path_prefix=normalized_path_prefix,
            language=normalized_language,
        )

        results: list[dict[str, Any]] = []
        citations: list[str] = []
        for item in search_results:
            citation = _format_search_citation(
                repo_id=item.citation.repo_id,
                path=item.citation.path,
                start_line=item.citation.start_line,
                end_line=item.citation.end_line,
            )
            citations.append(citation)
            results.append(
                {
                    "text": item.text,
                    "path": item.citation.path,
                    "start_line": item.citation.start_line,
                    "end_line": item.citation.end_line,
                    "score": item.citation.score,
                    "language": item.citation.language,
                    "chunk_type": item.citation.chunk_type,
                    "citation": citation,
                }
            )

        return {
            "query": normalized_query,
            "repo_id": normalized_repo_id,
            "results": results,
            "citations": citations,
        }

    def code_snippet(
        repo_id: str,
        path: str,
        start_line: int,
        end_line: int,
    ) -> dict[str, Any]:
        normalized_repo_id = _normalize_required(repo_id, field_name="repo_id")
        normalized_path = _normalize_required(path, field_name="path")
        if start_line < 1:
            raise ValueError("start_line must be >= 1")
        if end_line < 1:
            raise ValueError("end_line must be >= 1")
        if end_line < start_line:
            raise ValueError("end_line must be >= start_line")

        resolved_snippet_service = snippet_service or snippet_service_getter()
        snippet = resolved_snippet_service.fetch_snippet(
            normalized_repo_id,
            normalized_path,
            start_line=start_line,
            end_line=end_line,
        )
        return _snippet_response(repo_id=normalized_repo_id, path=normalized_path, snippet=snippet)

    async def code_search_lexical(
        query: str,
        repo_id: str,
        file_pattern: str | None = None,
        top_k: int = 10,
    ) -> dict[str, Any]:
        normalized_query = _normalize_required(query, field_name="query")
        normalized_repo_id = _normalize_required(repo_id, field_name="repo_id")
        normalized_file_pattern = _normalize_optional(file_pattern)
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        if top_k > MAX_TOP_K:
            raise ValueError(f"top_k must be <= {MAX_TOP_K}")

        resolved_zoekt_client = zoekt_client or zoekt_client_getter()
        if resolved_zoekt_client is None:
            return {
                "query": normalized_query,
                "repo_id": normalized_repo_id,
                "results": [],
                "citations": [],
                "error": "Zoekt is unavailable (ZOEKT_URL not configured)",
            }

        lexical_matches = await resolved_zoekt_client.search(
            normalized_query,
            num=top_k,
            file_pattern=normalized_file_pattern,
        )

        results: list[dict[str, Any]] = []
        citations: list[str] = []
        for file_match in lexical_matches:
            if file_match.repo_id != normalized_repo_id:
                continue
            for line_match in file_match.line_matches:
                result = _lexical_result(
                    repo_id=file_match.repo_id,
                    path=file_match.path,
                    score=file_match.score,
                    line_match=line_match,
                )
                results.append(result)
                citations.append(cast(str, result["citation"]))

        return {
            "query": normalized_query,
            "repo_id": normalized_repo_id,
            "results": results,
            "citations": citations,
            "error": None,
        }

    _register_tool(
        server=server,
        name="code_search",
        description="Semantic code search with optional repo/path/language filters",
        handler=code_search,
    )
    _register_tool(
        server=server,
        name="code_snippet",
        description="Fetch a repository-relative snippet by inclusive line range",
        handler=code_snippet,
    )
    _register_tool(
        server=server,
        name="code_search_lexical",
        description="Lexical/regex code search with Zoekt query syntax",
        handler=code_search_lexical,
    )
