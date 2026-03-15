"""
Retrieval MCP tools — thin wrappers for vector search operations.

Architecture rule:
    Agents (especially the Retrieval Agent) must NOT access EmbeddingService,
    VectorStoreService, or ChromaDB directly.
    All semantic search and chunk embedding goes through these functions.

Coordination:
    upsert_chunks    → EmbeddingService.embed_batch + VectorStoreService.upsert_chunks
    search_chunks    → EmbeddingService.embed + VectorStoreService.search_chunks
    get_chunks_by_ids → VectorStoreService.get_chunks_by_ids (no embedding)
    delete_document  → VectorStoreService.delete_document

Services are created lazily so environments without ChromaDB/Ollama can still
import this module without crashing (they will fail at call time instead).
"""

from __future__ import annotations

import logging
from typing import Optional

from src.app.schemas.retrieval import ChunkUpsert, SearchQuery, SearchResult
from src.app.services.embedding_service import EmbeddingService
from src.app.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)

# Singletons — shared across all agents for the same process lifetime.
# Replace in tests: retrieval_tools._embedding_svc = MockEmbeddingService(...)
_embedding_svc: Optional[EmbeddingService] = None
_vector_svc: Optional[VectorStoreService] = None


def _get_embedding_svc() -> EmbeddingService:
    global _embedding_svc
    if _embedding_svc is None:
        _embedding_svc = EmbeddingService()
    return _embedding_svc


def _get_vector_svc() -> VectorStoreService:
    global _vector_svc
    if _vector_svc is None:
        _vector_svc = VectorStoreService()
    return _vector_svc


# ------------------------------------------------------------------
# Write operations
# ------------------------------------------------------------------

def retrieval_upsert_chunks(chunks: list[dict]) -> int:
    """
    Embed and store a list of chunks in the vector store.

    Each dict must match ChunkUpsert schema:
        chunk_id, document_id, tenant_id, chunk_index, content

    Called during ingestion after content_save_chunks().

    Returns:
        Number of chunks successfully upserted.
    """
    parsed = [ChunkUpsert(**c) for c in chunks]
    if not parsed:
        return 0

    texts = [c.content for c in parsed]
    embeddings = _get_embedding_svc().embed_batch(texts)

    _get_vector_svc().upsert_chunks(parsed, embeddings)
    return len(parsed)


def retrieval_delete_document(document_id: str, tenant_id: str) -> None:
    """
    Remove all vector store entries for a document (e.g. on content update).

    Args:
        document_id: UUID of the document to remove from the vector store.
        tenant_id:   Tenant scope.
    """
    _get_vector_svc().delete_document(document_id, tenant_id)


# ------------------------------------------------------------------
# Search operations
# ------------------------------------------------------------------

def retrieval_search_chunks(
    query_text: str,
    tenant_id: str,
    filters: Optional[dict] = None,
    top_k: int = 5,
    score_threshold: Optional[float] = None,
) -> list[dict]:
    """
    Semantic similarity search over lesson chunks.

    Called by the Retrieval Agent and Tutor Agent to find relevant content.

    Args:
        query_text:      The user's question or search phrase.
        tenant_id:       Tenant scope (prevents cross-tenant leakage).
        filters:         Optional metadata filters (e.g. {"document_id": "..."}).
        top_k:           Max results to return (default 5).
        score_threshold: Minimum cosine similarity score (0.0 – 1.0).

    Returns:
        List of SearchResult dicts, sorted by score descending.
    """
    query_embedding = _get_embedding_svc().embed(query_text)

    results: list[SearchResult] = _get_vector_svc().search_chunks(
        query_embedding=query_embedding,
        tenant_id=tenant_id,
        filters=filters,
        top_k=top_k,
        score_threshold=score_threshold,
    )
    return [r.model_dump() for r in results]


def retrieval_get_chunks_by_ids(
    chunk_ids: list[str],
    tenant_id: str,
) -> list[dict]:
    """
    Fetch specific chunks by ID (no similarity ranking).

    Useful when an agent already knows which chunk IDs it needs.

    Args:
        chunk_ids: List of chunk UUIDs.
        tenant_id: Tenant scope.

    Returns:
        List of SearchResult dicts (score=1.0).
    """
    results = _get_vector_svc().get_chunks_by_ids(chunk_ids, tenant_id)
    return [r.model_dump() for r in results]
