-- ============================================================
-- DOCUMENT STORE
-- Migration: 002_document_store.sql
-- Run this in: Supabase Dashboard → SQL Editor
--
-- Creates 3 tables:
--   lessons           → catalogue of all lessons (metadata only)
--   lesson_chunks     → the actual text content, split into pieces
--   lesson_embeddings → one vector per chunk (for semantic search)
--
-- Also creates:
--   semantic_search() → function used by the Retrieval Agent (RAG)
-- ============================================================


-- ──────────────────────────────────────────────────────────
-- STEP 1: Enable pgvector
-- Required for the lesson_embeddings table.
-- Safe to run even if already enabled.
-- ──────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;


-- ──────────────────────────────────────────────────────────
-- TABLE 1: lessons
--
-- One row per lesson. Stores metadata only.
-- The actual text lives in lesson_chunks.
--
-- lesson_id is a human-readable slug, e.g. 'biology_ch1',
-- 'algebra_linear_eq'. Easier to reference than a UUID.
-- ──────────────────────────────────────────────────────────
CREATE TABLE lessons (
    lesson_id    TEXT PRIMARY KEY,  -- e.g. 'biology_ch1', 'math_fractions'

    -- What the lesson is about
    title        TEXT NOT NULL,
    description  TEXT,
    subject      TEXT NOT NULL,     -- 'Mathematics', 'Science', 'Language Arts'
    topic        TEXT NOT NULL,     -- 'Algebra', 'Photosynthesis', 'Grammar'
    grade_level  TEXT,              -- '6th', '10th', 'university'
    difficulty   TEXT NOT NULL DEFAULT 'medium'
                 CHECK (difficulty IN ('easy', 'medium', 'hard')),

    -- Where the content came from
    source_type  TEXT NOT NULL DEFAULT 'manual'
                 CHECK (source_type IN ('pdf', 'text', 'manual')),
    file_path    TEXT,              -- Supabase Storage path (if uploaded file)

    -- Counters — updated when chunks are added
    total_chunks INT  NOT NULL DEFAULT 0,

    -- Status flags
    is_published BOOLEAN NOT NULL DEFAULT FALSE, -- visible to students?
    is_indexed   BOOLEAN NOT NULL DEFAULT FALSE, -- embeddings generated?

    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Keep updated_at current
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_lessons_updated_at
    BEFORE UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX idx_lessons_subject  ON lessons(subject);
CREATE INDEX idx_lessons_topic    ON lessons(subject, topic);
CREATE INDEX idx_lessons_level    ON lessons(grade_level);
CREATE INDEX idx_lessons_published ON lessons(is_published) WHERE is_published = TRUE;


-- ──────────────────────────────────────────────────────────
-- TABLE 2: lesson_chunks
--
-- One row per text segment extracted from a lesson.
-- This is what agents actually read.
--
-- A lesson is split into chunks so that:
--   - The Retrieval Agent can return only the relevant parts
--   - The Tutor/Quiz Agents ground answers in specific sections
--   - Long documents don't overflow the LLM context window
-- ──────────────────────────────────────────────────────────
CREATE TABLE lesson_chunks (
    chunk_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id     TEXT NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,

    -- The actual text of this chunk
    content       TEXT NOT NULL,

    -- Where this chunk sits in the lesson
    chunk_index   INT  NOT NULL,    -- 0-based position within the lesson
    section_title TEXT,             -- e.g. 'Introduction', 'Key Concepts'

    -- What kind of content this is
    content_type  TEXT NOT NULL DEFAULT 'paragraph'
                  CHECK (content_type IN (
                      'paragraph',  -- normal prose
                      'definition', -- term being defined
                      'example',    -- worked example
                      'summary',    -- end-of-section summary
                      'list'        -- bullet/numbered list
                  )),

    -- Set at ingestion time, used by the Retrieval Agent to filter
    topic_tags    TEXT[],           -- micro-topics this chunk covers

    -- Flag: FALSE until an embedding is generated for this chunk
    is_embedded   BOOLEAN NOT NULL DEFAULT FALSE,

    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chunks_lesson     ON lesson_chunks(lesson_id);
CREATE INDEX idx_chunks_order      ON lesson_chunks(lesson_id, chunk_index);
CREATE INDEX idx_chunks_not_embedded ON lesson_chunks(is_embedded) WHERE is_embedded = FALSE;
CREATE INDEX idx_chunks_topic_tags ON lesson_chunks USING GIN(topic_tags);


-- ──────────────────────────────────────────────────────────
-- TABLE 3: lesson_embeddings
--
-- One row per chunk. Stores the vector representation of
-- that chunk's text for semantic (meaning-based) search.
--
-- Kept as a separate table so that:
--   - chunk rows exist before embeddings are ready
--   - non-vector queries on lesson_chunks stay fast
--
-- Default dimension: 384
--   → matches 'all-MiniLM-L6-v2' (local model, no API cost)
-- Change to 768 or 1536 if you switch to a larger model.
-- ──────────────────────────────────────────────────────────
CREATE TABLE lesson_embeddings (
    chunk_id    UUID        PRIMARY KEY REFERENCES lesson_chunks(chunk_id) ON DELETE CASCADE,
    lesson_id   TEXT        NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    embedding   VECTOR(384) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- HNSW index — fast approximate nearest-neighbor search
-- This is what makes semantic_search() fast.
CREATE INDEX idx_embeddings_hnsw
    ON lesson_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Update the chunk flag once an embedding is inserted
CREATE OR REPLACE FUNCTION mark_chunk_embedded()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE lesson_chunks
    SET is_embedded = TRUE
    WHERE chunk_id = NEW.chunk_id;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_mark_chunk_embedded
    AFTER INSERT ON lesson_embeddings
    FOR EACH ROW EXECUTE FUNCTION mark_chunk_embedded();


-- ──────────────────────────────────────────────────────────
-- FUNCTION: semantic_search
--
-- Called by the Retrieval Agent.
-- Takes the embedding of the user's question and returns
-- the most relevant lesson chunks by cosine similarity.
--
-- Parameters:
--   query_embedding  → the vector of the user's question
--   filter_lesson_id → optional, restrict to one lesson
--   match_count      → how many chunks to return (default 5)
--   min_similarity   → minimum match quality 0.0–1.0 (default 0.5)
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION semantic_search(
    query_embedding   VECTOR(384),
    filter_lesson_id  TEXT    DEFAULT NULL,
    match_count       INT     DEFAULT 5,
    min_similarity    FLOAT8  DEFAULT 0.5
)
RETURNS TABLE (
    chunk_id      UUID,
    lesson_id     TEXT,
    content       TEXT,
    section_title TEXT,
    topic_tags    TEXT[],
    similarity    FLOAT8
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        lc.chunk_id,
        lc.lesson_id,
        lc.content,
        lc.section_title,
        lc.topic_tags,
        (1 - (le.embedding <=> query_embedding))::FLOAT8 AS similarity
    FROM lesson_embeddings le
    JOIN lesson_chunks lc ON le.chunk_id = lc.chunk_id
    WHERE
        (filter_lesson_id IS NULL OR lc.lesson_id = filter_lesson_id)
        AND (1 - (le.embedding <=> query_embedding)) >= min_similarity
    ORDER BY le.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;


-- ──────────────────────────────────────────────────────────
-- ROW LEVEL SECURITY
--
-- Lessons: any logged-in user can read published lessons.
-- Writes: backend only (service_role key).
-- ──────────────────────────────────────────────────────────
ALTER TABLE lessons           ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_chunks     ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_embeddings ENABLE ROW LEVEL SECURITY;

-- Students can read published lessons
CREATE POLICY "read_published_lessons"
    ON lessons FOR SELECT TO authenticated
    USING (is_published = TRUE);

-- Students can read all chunks (lesson access is controlled via lessons table)
CREATE POLICY "read_lesson_chunks"
    ON lesson_chunks FOR SELECT TO authenticated
    USING (TRUE);

-- Students can read embeddings (needed for semantic_search to work)
CREATE POLICY "read_lesson_embeddings"
    ON lesson_embeddings FOR SELECT TO authenticated
    USING (TRUE);

-- Only the backend (service_role) can write to any of these tables
CREATE POLICY "backend_write_lessons"
    ON lessons FOR ALL TO service_role
    USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "backend_write_chunks"
    ON lesson_chunks FOR ALL TO service_role
    USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "backend_write_embeddings"
    ON lesson_embeddings FOR ALL TO service_role
    USING (TRUE) WITH CHECK (TRUE);
