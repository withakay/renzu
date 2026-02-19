"""Code indexing module for parsing and embedding source code."""

from app.indexing.chunker import Chunk, Chunker, TreeSitterChunker
from app.indexing.embedder import (
    CacheEmbedder,
    EmbeddingProvider,
    OpenAIEmbedder,
    create_embedder,
    get_embedder,
)
from app.indexing.pipeline import IndexingPipeline, IndexingResult
from app.indexing.qdrant import ChunkPayload, ChunkPoint, QdrantClient, get_qdrant_client
from app.indexing.walker import FileInfo, FileWalker

__all__ = [
    "CacheEmbedder",
    "Chunk",
    "ChunkPayload",
    "ChunkPoint",
    "Chunker",
    "EmbeddingProvider",
    "FileInfo",
    "FileWalker",
    "IndexingPipeline",
    "IndexingResult",
    "OpenAIEmbedder",
    "QdrantClient",
    "TreeSitterChunker",
    "create_embedder",
    "get_embedder",
    "get_qdrant_client",
]
