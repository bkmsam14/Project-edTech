"""
VectorStoreService — persistent vector store built on ChromaDB.

Stores content chunk embeddings and provides semantic similarity search.
Works in tandem with ContentService (Supabase) which stores the metadata.

Architecture rule:
    Agents must NOT access ChromaDB directly.
    All vector search and upsert operations go through VectorStoreService
    (or RetrievalTool which wraps it).

ChromaDB collection name: "content_chunks"
Embedding dimension:       768 (nomic-embed-text)
Persistence:               local directory (configurable, default ./chroma_data)
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from src.app.schemas.retrieval import ChunkUpsert, SearchResult

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "content_chunks"


class VectorStoreService:
    """
    Persistent vector store for lesson content chunks.

    Usage:
        svc = VectorStoreService()
        svc.upsert_chunks(chunks, embeddings)
        results = svc.search_chunks(query_embedding, tenant_id="t1", top_k=5)
    """

    def __init__(self, persist_dir: str = "./chroma_data") -> None:
        """
        Args:
            persist_dir: Local directory where ChromaDB stores data.
        """
        try:
            import chromadb  # soft dependency — only needed at runtime
            os.makedirs(persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "VectorStoreService ready — collection=%s dir=%s",
                _COLLECTION_NAME, persist_dir,
            )
        except ImportError as exc:
            raise ImportError(
                "chromadb is required for VectorStoreService. "
                "Install it with:  pip install chromadb"
            ) from exc

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def upsert_chunks(
        self,
        chunks: list[ChunkUpsert],
        embeddings: list[list[float]],
    ) -> None:
        """
        Add or update chunk embeddings in the vector store.

        Args:
            chunks:     List of ChunkUpsert — metadata and content.
            embeddings: Precomputed embedding vectors (same order as chunks).

        Raises:
            ValueError: If chunks and embeddings differ in length.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) "
                "must have the same length"
            )
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [
            {
                "document_id": c.document_id,
                "tenant_id": c.tenant_id,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ]

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info("upserted %d chunks into vector store", len(chunks))

    def delete_document(self, document_id: str, tenant_id: str) -> None:
        """
        Remove all chunks belonging to a document from the vector store.

        Args:
            document_id: UUID of the document whose chunks to remove.
            tenant_id:   Tenant scope for the deletion.
        """
        self._collection.delete(
            where={"$and": [
                {"document_id": {"$eq": document_id}},
                {"tenant_id": {"$eq": tenant_id}},
            ]}
        )
        logger.info("deleted chunks for document_id=%s tenant=%s", document_id, tenant_id)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def search_chunks(
        self,
        query_embedding: list[float],
        tenant_id: str,
        filters: Optional[dict] = None,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> list[SearchResult]:
        """
        Run a cosine similarity search against stored chunk embeddings.

        Args:
            query_embedding: Embedding vector of the search query.
            tenant_id:       Tenant scope (mandatory — prevents cross-tenant leakage).
            filters:         Optional extra filters (e.g. {"document_id": "..."}).
            top_k:           Max results to return.
            score_threshold: Minimum similarity score (0 = unfiltered).

        Returns:
            List of SearchResult, sorted by score descending.
        """
        where_clause: dict = {"tenant_id": {"$eq": tenant_id}}

        if filters:
            extra = [
                {k: {"$eq": v}} for k, v in filters.items()
            ]
            where_clause = {"$and": [{"tenant_id": {"$eq": tenant_id}}, *extra]}

        response = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        results = []
        ids = response["ids"][0]
        docs = response["documents"][0]
        metas = response["metadatas"][0]
        # ChromaDB cosine distance → similarity = 1 - distance
        distances = response["distances"][0]

        for chunk_id, content, meta, dist in zip(ids, docs, metas, distances):
            score = round(1.0 - dist, 4)
            if score_threshold is not None and score < score_threshold:
                continue
            results.append(SearchResult(
                chunk_id=chunk_id,
                document_id=meta.get("document_id", ""),
                tenant_id=meta.get("tenant_id", tenant_id),
                content=content,
                score=score,
                chunk_index=int(meta.get("chunk_index", 0)),
                metadata=meta,
            ))

        return results

    def get_chunks_by_ids(
        self,
        chunk_ids: list[str],
        tenant_id: str,
    ) -> list[SearchResult]:
        """
        Fetch specific chunks by their IDs (no similarity search).

        Args:
            chunk_ids: List of chunk UUIDs to fetch.
            tenant_id: Tenant scope (used only for building the return model).

        Returns:
            List of SearchResult (score=1.0 since no ranking applied).
        """
        if not chunk_ids:
            return []

        response = self._collection.get(
            ids=chunk_ids,
            include=["documents", "metadatas"],
        )

        results = []
        for chunk_id, content, meta in zip(
            response["ids"], response["documents"], response["metadatas"]
        ):
            results.append(SearchResult(
                chunk_id=chunk_id,
                document_id=meta.get("document_id", ""),
                tenant_id=meta.get("tenant_id", tenant_id),
                content=content,
                score=1.0,
                chunk_index=int(meta.get("chunk_index", 0)),
                metadata=meta,
            ))
        return results
