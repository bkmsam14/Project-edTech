"""
ContentService — Supabase-backed store for documents and text chunks.

Architecture rule:
    Agents must NOT query the documents or content_chunks tables directly.
    All content metadata reads/writes go through ContentService (or ContentTool).

Vector embeddings are managed separately by VectorStoreService (ChromaDB).
This service handles the metadata side: document registry and raw chunk text.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.app.schemas.content import ChunkCreate, ChunkOut, DocumentCreate, DocumentOut

logger = logging.getLogger(__name__)


class ContentService:
    """
    Manages document metadata and raw text chunks in Supabase.

    Usage:
        from src.database.client import supabase_admin
        service = ContentService(supabase_admin)
    """

    def __init__(self, client: Any) -> None:
        self._db = client

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def save_document(self, doc: DocumentCreate) -> DocumentOut:
        """
        Register a new document (lesson/article) in the content store.

        Args:
            doc: DocumentCreate — metadata fields.

        Returns:
            DocumentOut with the generated UUID and created_at timestamp.
        """
        payload = doc.model_dump(exclude_none=True)
        response = self._db.table("documents").insert(payload).execute()
        row = response.data[0]
        logger.info("document saved id=%s title=%s", row.get("id"), doc.title)
        return DocumentOut(**row)

    def get_document(self, document_id: str) -> Optional[DocumentOut]:
        """
        Fetch a single document by its UUID.

        Args:
            document_id: UUID of the document.

        Returns:
            DocumentOut or None if not found.
        """
        response = (
            self._db.table("documents")
            .select("*")
            .eq("id", document_id)
            .execute()
        )
        return DocumentOut(**response.data[0]) if response.data else None

    def list_lessons(
        self,
        tenant_id: str,
        course_id: Optional[str] = None,
    ) -> list[DocumentOut]:
        """
        List all documents for a tenant, optionally filtered by course.

        Args:
            tenant_id: Tenant identifier.
            course_id: Optional course scope.

        Returns:
            List of DocumentOut, ordered by created_at descending.
        """
        query = (
            self._db.table("documents")
            .select("*")
            .eq("tenant_id", tenant_id)
            .order("created_at", desc=True)
        )
        if course_id is not None:
            query = query.eq("course_id", course_id)

        response = query.execute()
        return [DocumentOut(**row) for row in (response.data or [])]

    # ------------------------------------------------------------------
    # Chunks
    # ------------------------------------------------------------------

    def save_chunks(
        self,
        document_id: str,
        chunks: list[ChunkCreate],
    ) -> list[ChunkOut]:
        """
        Bulk-insert text chunks linked to a document.

        Args:
            document_id: UUID of the parent document.
            chunks:      List of ChunkCreate — one per text segment.

        Returns:
            List of inserted ChunkOut rows.
        """
        if not chunks:
            return []

        rows = [
            {"document_id": document_id, **c.model_dump(exclude_none=True)}
            for c in chunks
        ]
        response = self._db.table("content_chunks").insert(rows).execute()
        logger.info(
            "chunks saved document_id=%s count=%d", document_id, len(response.data)
        )
        return [ChunkOut(**row) for row in response.data]

    def get_chunks(self, document_id: str) -> list[ChunkOut]:
        """
        Fetch all chunks for a document, ordered by chunk_index.

        Args:
            document_id: UUID of the parent document.

        Returns:
            List of ChunkOut, sorted by chunk_index ascending.
        """
        response = (
            self._db.table("content_chunks")
            .select("*")
            .eq("document_id", document_id)
            .order("chunk_index")
            .execute()
        )
        return [ChunkOut(**row) for row in (response.data or [])]
