-- ============================================================
-- NeuroLearn Content Schema
-- Migration: 002_content_schema
--
-- Tables:
--   1. documents      - lesson/document metadata
--   2. content_chunks - raw text chunks (metadata side)
--                       Vector embeddings live in ChromaDB.
-- ============================================================

-- ----------------------------------------------------------------
-- Drop in reverse dependency order (safe to re-run)
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS content_chunks CASCADE;
DROP TABLE IF EXISTS documents       CASCADE;

-- ----------------------------------------------------------------
-- 1. documents
-- ----------------------------------------------------------------
CREATE TABLE documents (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   text        NOT NULL,
    course_id   text,
    lesson_id   text,
    title       text        NOT NULL,
    subject     text,
    difficulty  text,
    tags        jsonb,
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------
-- 2. content_chunks
-- ----------------------------------------------------------------
CREATE TABLE content_chunks (
    id            uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id   uuid        NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tenant_id     text        NOT NULL,
    chunk_index   integer     NOT NULL,
    content       text        NOT NULL,
    token_count   integer,
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------
-- Indexes
-- ----------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_docs_tenant
    ON documents (tenant_id);

CREATE INDEX IF NOT EXISTS idx_docs_tenant_course
    ON documents (tenant_id, course_id);

CREATE INDEX IF NOT EXISTS idx_chunks_document
    ON content_chunks (document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_tenant_document
    ON content_chunks (tenant_id, document_id);
