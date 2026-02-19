"""Retrieval module for vector search and context assembly."""

from app.retrieval.search import Citation, SearchResult, SearchService, get_search_service
from app.retrieval.snippet import SnippetError, SnippetService, get_snippet_service

__all__ = [
    "Citation",
    "SearchResult",
    "SearchService",
    "SnippetError",
    "SnippetService",
    "get_search_service",
    "get_snippet_service",
]
