"""
Pydantic schemas for Retrieval tooling.

Shared between EmbeddingService, VectorStoreService, and RetrievalTool.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ChunkUpsert(BaseModel):
    """A chunk to embed and store in the vector store."""

    chunk_id: str                       # UUID from content_chunks.id
    document_id: str
    tenant_id: str
    chunk_index: int
    content: str


class SearchQuery(BaseModel):
    """Query parameters for vector similarity search."""

    query_text: str
    tenant_id: str
    filters: Optional[dict] = None      # e.g. {"document_id": "..."}
    top_k: int = Field(default=5, ge=1, le=50)
    score_threshold: Optional[float] = None  # minimum similarity score (0-1)


class SearchResult(BaseModel):
    """A single result row from a vector search."""

    chunk_id: str
    document_id: str
    tenant_id: str
    content: str
    score: float                        # cosine similarity (higher = more relevant)
    chunk_index: int
    metadata: dict = {}
