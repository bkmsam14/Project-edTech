"""
Pydantic schemas for Content tooling.

Used by ContentTool and ContentService to define the contract for
document and chunk read/write operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    """Metadata required to register a new document/lesson."""

    tenant_id: str
    title: str
    course_id: Optional[str] = None
    lesson_id: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None    # beginner | developing | proficient | advanced
    tags: Optional[list[str]] = None


class DocumentOut(BaseModel):
    """Document row as returned from the database."""

    id: str
    tenant_id: str
    title: str
    course_id: Optional[str] = None
    lesson_id: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[list[str]] = None
    created_at: Optional[datetime] = None


class ChunkCreate(BaseModel):
    """A single text chunk to be stored under a document."""

    tenant_id: str
    chunk_index: int
    content: str
    token_count: Optional[int] = None


class ChunkOut(BaseModel):
    """Content chunk row as returned from the database."""

    id: str
    document_id: str
    tenant_id: str
    chunk_index: int
    content: str
    token_count: Optional[int] = None
    created_at: Optional[datetime] = None
