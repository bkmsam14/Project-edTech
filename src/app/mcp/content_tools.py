"""
Content MCP tools — thin wrappers exposing ContentService to agents.

Architecture rule:
    Agents must NOT query documents or content_chunks tables directly.
    All content metadata operations go through these functions.

    Note: vector search uses retrieval_tools, not this module.
    This module is for metadata: registering documents and storing raw chunks.
"""

from __future__ import annotations

from typing import Optional

from src.app.schemas.content import ChunkCreate, DocumentCreate
from src.app.services.content_service import ContentService
from src.database.client import supabase_admin

_service = ContentService(supabase_admin)


def content_save_document(
    tenant_id: str,
    title: str,
    course_id: Optional[str] = None,
    lesson_id: Optional[str] = None,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """
    Register a new document/lesson in the content store.

    Called by the ingestion pipeline when new learning material is added.

    Returns:
        Serialised DocumentOut dict with the generated document UUID.
    """
    doc = DocumentCreate(
        tenant_id=tenant_id,
        title=title,
        course_id=course_id,
        lesson_id=lesson_id,
        subject=subject,
        difficulty=difficulty,
        tags=tags,
    )
    return _service.save_document(doc).model_dump()


def content_get_document(document_id: str) -> Optional[dict]:
    """
    Fetch document metadata by UUID.

    Returns:
        Serialised DocumentOut dict, or None if not found.
    """
    result = _service.get_document(document_id)
    return result.model_dump() if result else None


def content_list_lessons(
    tenant_id: str,
    course_id: Optional[str] = None,
) -> list[dict]:
    """
    List all documents for a tenant, optionally filtered by course.

    Called by the Retrieval Agent and Recommendation Agent to discover
    available content.

    Returns:
        List of serialised DocumentOut dicts, newest first.
    """
    return [d.model_dump() for d in _service.list_lessons(tenant_id, course_id)]


def content_save_chunks(
    document_id: str,
    chunks: list[dict],
) -> list[dict]:
    """
    Bulk-store text chunks for a document.

    Each dict in `chunks` must match ChunkCreate schema:
        tenant_id, chunk_index, content, token_count?

    Called during ingestion after chunking the raw document text.
    After saving, call retrieval_upsert_chunks() to embed them.

    Returns:
        List of serialised ChunkOut dicts with generated UUIDs.
    """
    parsed = [ChunkCreate(**c) for c in chunks]
    return [ch.model_dump() for ch in _service.save_chunks(document_id, parsed)]


def content_get_chunks(document_id: str) -> list[dict]:
    """
    Fetch all raw text chunks for a document, ordered by chunk_index.

    Returns:
        List of serialised ChunkOut dicts.
    """
    return [ch.model_dump() for ch in _service.get_chunks(document_id)]
