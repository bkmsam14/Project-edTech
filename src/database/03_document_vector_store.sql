-- ============================================================
-- DOCUMENT STORE + VECTOR STORE
-- Supabase / PostgreSQL + pgvector
--
-- Contains:
--   1. lessons         → lesson metadata catalogue
--   2. lesson_chunks   → extracted text chunks from lessons
--   3. lesson_embeddings → vector embeddings (pgvector)
--                          for semantic search (RAG)
--
-- Used by:
--   → Retrieval Agent  (reads chunks + embeddings for RAG)
--   → Quiz Agent       (reads lesson chunks to generate questions)
--   → Tutor Agent      (grounds explanations in lesson content)
-- ============================================================


-- ──────────────────────────────────────────────
-- PREREQUISITE: Enable pgvector extension
-- Run this once in Supabase SQL editor
-- ──────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;


-- ──────────────────────────────────────────────
-- TABLE 1: lessons
-- Metadata catalogue for all lessons.
-- One row per lesson (not per chunk).
-- ──────────────────────────────────────────────
CREATE TABLE lessons (
    lesson_id       TEXT PRIMARY KEY,              -- e.g. 'biology_101', 'algebra_ch3'
    title           TEXT NOT NULL,
    description     TEXT,

    -- Classification
    subject         TEXT NOT NULL,                 -- 'Mathematics', 'Science', 'Language Arts'
    topic           TEXT NOT NULL,                 -- 'Algebra', 'Photosynthesis'
    subtopic        TEXT,                          -- 'Linear Equations'
    grade_level     TEXT,                          -- '6th', '10th', 'university'
    difficulty      TEXT DEFAULT 'medium'
                    CHECK (difficulty IN ('easy', 'medium', 'hard')),

    -- Source
    source_type     TEXT CHECK (source_type IN ('pdf', 'text', 'video', 'web', 'manual')),
    source_url      TEXT,
    file_path       TEXT,                          -- Path in Supabase Storage

    -- Content Stats
    total_chunks    INT DEFAULT 0,
    word_count      INT DEFAULT 0,
    estimated_read_minutes INT DEFAULT 0,

    -- Status
    is_published    BOOLEAN DEFAULT FALSE,
    is_indexed      BOOLEAN DEFAULT FALSE,         -- TRUE once embeddings are generated

    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lessons IS
    'Lesson metadata catalogue. The actual content lives in lesson_chunks.';

CREATE INDEX idx_lessons_subject_topic ON lessons(subject, topic);
CREATE INDEX idx_lessons_difficulty    ON lessons(difficulty);
CREATE INDEX idx_lessons_published     ON lessons(is_published) WHERE is_published = TRUE;


-- ──────────────────────────────────────────────
-- TABLE 2: lesson_chunks
-- Extracted text segments from each lesson.
-- Each chunk is a semantically meaningful piece
-- of content (paragraph, heading + paragraph, etc.)
-- ──────────────────────────────────────────────
CREATE TABLE lesson_chunks (
    chunk_id        TEXT PRIMARY KEY,              -- e.g. 'biology_101_chunk_003'
    lesson_id       TEXT NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,

    -- Content
    content         TEXT NOT NULL,                 -- The actual text
    content_type    TEXT DEFAULT 'paragraph'
                    CHECK (content_type IN (
                        'paragraph', 'definition', 'example',
                        'summary', 'heading', 'list', 'formula'
                    )),

    -- Position in the lesson
    chunk_index     INT NOT NULL,                  -- Order within the lesson
    page_number     INT,                           -- If from PDF
    section_title   TEXT,                          -- Heading this chunk belongs to

    -- Tags (set during ingestion, used for retrieval filtering)
    topic_tags      TEXT[],                        -- Micro-topics this chunk covers
    keyword_tags    TEXT[],                        -- Important keywords

    -- Stats
    word_count      INT DEFAULT 0,
    is_indexed      BOOLEAN DEFAULT FALSE,         -- TRUE once embedding exists

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lesson_chunks IS
    'Extracted text chunks from lessons. Each chunk gets an embedding
     in lesson_embeddings for semantic search.';

CREATE INDEX idx_chunks_lesson      ON lesson_chunks(lesson_id);
CREATE INDEX idx_chunks_order       ON lesson_chunks(lesson_id, chunk_index);
CREATE INDEX idx_chunks_topic_tags  ON lesson_chunks USING GIN(topic_tags);
CREATE INDEX idx_chunks_not_indexed ON lesson_chunks(is_indexed) WHERE is_indexed = FALSE;


-- ──────────────────────────────────────────────
-- TABLE 3: lesson_embeddings
-- Vector embeddings for semantic similarity search.
-- Uses pgvector. One row per chunk.
-- ──────────────────────────────────────────────
CREATE TABLE lesson_embeddings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id        TEXT NOT NULL REFERENCES lesson_chunks(chunk_id) ON DELETE CASCADE,
    lesson_id       TEXT NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,

    -- The embedding vector
    -- 1536 dimensions = OpenAI text-embedding-ada-002
    -- 384 dimensions  = sentence-transformers/all-MiniLM-L6-v2 (local, free)
    -- 768 dimensions  = sentence-transformers/all-mpnet-base-v2 (local, better quality)
    embedding       VECTOR(384) NOT NULL,          -- Change to 768 or 1536 to match your model

    -- Which model generated this embedding
    model_name      TEXT DEFAULT 'all-MiniLM-L6-v2',

    created_at      TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(chunk_id)
);

COMMENT ON TABLE lesson_embeddings IS
    'Vector embeddings for semantic search.
     Dimension must match the embedding model used.
     Default: 384-dim for all-MiniLM-L6-v2 (local, no API cost).';


-- ── HNSW Index for fast approximate nearest-neighbor search ──
-- This is what makes semantic search fast at scale.
CREATE INDEX idx_embeddings_hnsw
    ON lesson_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Alternative: IVFFlat (faster to build, slightly less accurate)
-- CREATE INDEX idx_embeddings_ivfflat
--     ON lesson_embeddings
--     USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);


-- ──────────────────────────────────────────────
-- FUNCTION: semantic_search
-- Called by the Retrieval Agent to find the most
-- relevant chunks for a given query embedding.
-- ──────────────────────────────────────────────
CREATE OR REPLACE FUNCTION semantic_search(
    query_embedding  VECTOR(384),   -- The embedding of the user's question
    lesson_id_filter TEXT DEFAULT NULL,  -- Optionally restrict to one lesson
    match_count      INT DEFAULT 5,      -- How many chunks to return
    min_similarity   FLOAT DEFAULT 0.5   -- Minimum cosine similarity threshold
)
RETURNS TABLE (
    chunk_id        TEXT,
    lesson_id       TEXT,
    content         TEXT,
    section_title   TEXT,
    topic_tags      TEXT[],
    similarity      FLOAT
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
        1 - (le.embedding <=> query_embedding) AS similarity
    FROM lesson_embeddings le
    JOIN lesson_chunks lc ON le.chunk_id = lc.chunk_id
    WHERE
        (lesson_id_filter IS NULL OR lc.lesson_id = lesson_id_filter)
        AND 1 - (le.embedding <=> query_embedding) >= min_similarity
    ORDER BY le.embedding <=> query_embedding   -- closest first
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION semantic_search IS
    'Called by the Retrieval Agent.
     Pass the embedding of the users question and get back the top N
     most relevant lesson chunks by cosine similarity.

     Usage:
       SELECT * FROM semantic_search(
           query_embedding  := <your_vector>,
           lesson_id_filter := ''biology_101'',
           match_count      := 5,
           min_similarity   := 0.5
       );
    ';


-- ──────────────────────────────────────────────
-- ROW LEVEL SECURITY
-- Lessons are readable by all authenticated users.
-- Only admins/system can write.
-- ──────────────────────────────────────────────
ALTER TABLE lessons            ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_chunks      ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_embeddings  ENABLE ROW LEVEL SECURITY;

-- Anyone logged in can read lessons
CREATE POLICY "authenticated_read_lessons"
    ON lessons FOR SELECT
    TO authenticated
    USING (is_published = TRUE);

CREATE POLICY "authenticated_read_chunks"
    ON lesson_chunks FOR SELECT
    TO authenticated
    USING (TRUE);

CREATE POLICY "authenticated_read_embeddings"
    ON lesson_embeddings FOR SELECT
    TO authenticated
    USING (TRUE);

-- Only service_role (backend) can write
CREATE POLICY "service_write_lessons"
    ON lessons FOR ALL
    TO service_role
    USING (TRUE);

CREATE POLICY "service_write_chunks"
    ON lesson_chunks FOR ALL
    TO service_role
    USING (TRUE);

CREATE POLICY "service_write_embeddings"
    ON lesson_embeddings FOR ALL
    TO service_role
    USING (TRUE);
