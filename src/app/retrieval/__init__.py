"""Retrieval module for vector search and context assembly."""

from app.retrieval.search import Citation, SearchResult, SearchService, get_search_service

__all__ = [
    "Citation",
    "SearchResult",
    "SearchService",
    "get_search_service",
]
