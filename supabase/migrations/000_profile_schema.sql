-- ============================================================
-- PROFILE DB
-- Supabase / PostgreSQL
--
-- Contains:
--   1. users                   -> core identity (extends Supabase Auth)
--   2. support_settings        -> disability type + active support mode
--   3. accessibility_settings  -> dyslexia font/color/TTS preferences
--   4. learning_preferences    -> pace, format, gamification
--
-- Run order: 000 (this file) -> 001_analytics_schema -> 002_content_schema
--
-- The Learner Profile Module reads from ALL 4 tables and
-- assembles a single profile dict for the orchestrator context.
-- ============================================================

-- ----------------------------------------------------------------
-- Drop in reverse dependency order (safe to re-run)
-- Dropping a table cascades to its triggers, policies, and indexes.
-- ----------------------------------------------------------------
DROP TABLE IF EXISTS learning_preferences   CASCADE;
DROP TABLE IF EXISTS accessibility_settings CASCADE;
DROP TABLE IF EXISTS support_settings       CASCADE;
DROP TABLE IF EXISTS users                  CASCADE;


-- ──────────────────────────────────────────────
-- TABLE 1: users
-- Core user/student table - standalone (no auth dependency)
-- Can optionally link to Supabase Auth via auth_user_id
-- ──────────────────────────────────────────────
CREATE TABLE users (
    -- Primary user ID (standalone, not dependent on auth schema)
    user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Optional link to Supabase Auth (can be NULL if not using Supabase Auth)
    auth_user_id  UUID UNIQUE,

    -- Basic Info
    full_name     TEXT NOT NULL,
    username      TEXT UNIQUE,
    email         TEXT UNIQUE,
    avatar_url    TEXT,
    age_group     TEXT CHECK (age_group IN ('child', 'teen', 'adult')),
    grade_level   TEXT,                            -- e.g. '6th', '10th', 'university'
    language      TEXT DEFAULT 'en',               -- UI + content language

    -- Learning Level (updated by Assessment Agent over time)
    learning_level TEXT DEFAULT 'beginner'
                   CHECK (learning_level IN ('beginner', 'intermediate', 'advanced')),

    -- Onboarding
    onboarding_completed BOOLEAN DEFAULT FALSE,
    is_active            BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

COMMENT ON TABLE users IS
    'Core student profile. Standalone table - works with or without Supabase Auth.';
COMMENT ON COLUMN users.auth_user_id IS
    'Optional link to auth.users(id) if using Supabase Auth.';
COMMENT ON COLUMN users.learning_level IS
    'Updated by the Assessment Agent after quiz evaluation.';


-- ──────────────────────────────────────────────
-- TABLE 2: support_settings
-- Disability type + active support mode.
-- This is what the Orchestrator reads first to
-- decide which accessibility pipeline to invoke.
-- ──────────────────────────────────────────────
CREATE TABLE support_settings (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    support_mode     TEXT NOT NULL DEFAULT 'standard'
                     CHECK (support_mode IN (
                         'standard',
                         'dyslexia',
                         'adhd',
                         'dyscalculia',
                         'visual_impairment',
                         'hearing_impairment'
                     )),

    disability_types TEXT[],
    severity         TEXT DEFAULT 'moderate'
                     CHECK (severity IN ('mild', 'moderate', 'severe')),
    support_active   BOOLEAN DEFAULT TRUE,

    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);

COMMENT ON TABLE support_settings IS
    'Stores the student''s disability type and active support mode.
     Read by the Orchestrator at the start of every workflow.';
COMMENT ON COLUMN support_settings.support_mode IS
    'The primary mode that drives the Accessibility Agent pipeline.';
COMMENT ON COLUMN support_settings.severity IS
    'Calibrates how aggressively the Accessibility Agent simplifies content.';


-- ──────────────────────────────────────────────
-- TABLE 3: accessibility_settings
-- All rendering and readability preferences.
-- Read by the Accessibility Agent to adapt
-- every response for the student's disability.
-- ──────────────────────────────────────────────
CREATE TABLE accessibility_settings (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Font
    font_family             TEXT    DEFAULT 'OpenDyslexic',
    font_size_px            INT     DEFAULT 18
                            CHECK (font_size_px BETWEEN 12 AND 36),
    bold_text               BOOLEAN DEFAULT FALSE,

    -- Spacing
    line_spacing            NUMERIC(3,1) DEFAULT 2.0
                            CHECK (line_spacing BETWEEN 1.0 AND 3.0),
    letter_spacing_em       NUMERIC(3,2) DEFAULT 0.10,
    word_spacing_em         NUMERIC(3,2) DEFAULT 0.20,
    paragraph_gap_px        INT     DEFAULT 24,

    -- Colors
    color_scheme            TEXT DEFAULT 'cream'
                            CHECK (color_scheme IN (
                                'cream', 'high_contrast', 'dark_mode',
                                'pastel_blue', 'standard'
                            )),
    background_color_hex    TEXT DEFAULT '#FFFEF0',
    text_color_hex          TEXT DEFAULT '#333333',
    highlight_color_hex     TEXT DEFAULT '#FFFF99',

    -- Text Simplification
    text_chunking           TEXT DEFAULT 'short_sentences'
                            CHECK (text_chunking IN (
                                'none', 'short_sentences', 'single_idea_per_line'
                            )),
    max_sentence_words      INT  DEFAULT 15,
    simplified_vocabulary   BOOLEAN DEFAULT TRUE,
    use_bullet_points       BOOLEAN DEFAULT TRUE,
    use_numbered_steps      BOOLEAN DEFAULT TRUE,

    -- Reading Aids
    use_tts                 BOOLEAN DEFAULT FALSE,
    tts_speed               NUMERIC(3,2) DEFAULT 1.0
                            CHECK (tts_speed BETWEEN 0.5 AND 2.0),
    tts_voice               TEXT DEFAULT 'default',
    reading_ruler           BOOLEAN DEFAULT FALSE,
    word_highlighting       BOOLEAN DEFAULT FALSE,

    -- Visual Aids
    show_images             BOOLEAN DEFAULT TRUE,
    show_diagrams           BOOLEAN DEFAULT TRUE,
    reduce_visual_clutter   BOOLEAN DEFAULT TRUE,

    -- Interaction
    prefer_multiple_choice  BOOLEAN DEFAULT TRUE,
    prefer_visual_questions BOOLEAN DEFAULT TRUE,
    show_hints              BOOLEAN DEFAULT TRUE,

    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);

COMMENT ON TABLE accessibility_settings IS
    'All rendering preferences for the Accessibility Agent.
     Determines how text, fonts, colors, and interaction are adapted
     for a student''s disability type.';


-- ──────────────────────────────────────────────
-- TABLE 4: learning_preferences
-- How the student likes to learn.
-- Read by the Tutor Agent, Quiz Agent, and
-- Recommendation Agent.
-- ──────────────────────────────────────────────
CREATE TABLE learning_preferences (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                  UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    learning_style           TEXT DEFAULT 'visual'
                             CHECK (learning_style IN (
                                 'visual', 'auditory', 'reading_writing',
                                 'kinesthetic', 'mixed'
                             )),

    preferred_formats        TEXT[] DEFAULT ARRAY['text', 'visual'],

    explanation_style        TEXT DEFAULT 'step_by_step'
                             CHECK (explanation_style IN (
                                 'concise', 'step_by_step',
                                 'analogy_based', 'example_first'
                             )),

    learning_pace            TEXT DEFAULT 'moderate'
                             CHECK (learning_pace IN ('slow', 'moderate', 'fast', 'adaptive')),
    session_length_minutes   INT  DEFAULT 30
                             CHECK (session_length_minutes BETWEEN 5 AND 120),
    break_every_minutes      INT  DEFAULT 20,
    daily_goal_minutes       INT  DEFAULT 60,

    difficulty_preference    TEXT DEFAULT 'adaptive'
                             CHECK (difficulty_preference IN (
                                 'easy', 'moderate', 'challenging', 'adaptive'
                             )),

    quiz_frequency           TEXT DEFAULT 'after_each_lesson'
                             CHECK (quiz_frequency IN (
                                 'after_each_lesson', 'daily', 'weekly', 'on_demand'
                             )),
    instant_feedback         BOOLEAN DEFAULT TRUE,
    show_correct_answers     BOOLEAN DEFAULT TRUE,
    max_questions_per_quiz   INT     DEFAULT 5,

    enable_gamification      BOOLEAN DEFAULT TRUE,
    show_progress_bars       BOOLEAN DEFAULT TRUE,
    enable_badges            BOOLEAN DEFAULT TRUE,
    enable_streaks           BOOLEAN DEFAULT TRUE,

    created_at               TIMESTAMPTZ DEFAULT NOW(),
    updated_at               TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);

COMMENT ON TABLE learning_preferences IS
    'Tracks how the student prefers to receive and interact with content.
     The Tutor Agent and Quiz Agent use this to shape their output style.';


-- ──────────────────────────────────────────────
-- AUTO-UPDATE TRIGGER
-- Keeps updated_at current on all 4 tables.
-- CREATE OR REPLACE is safe to re-run.
-- ──────────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_support_settings_updated_at
    BEFORE UPDATE ON support_settings
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_accessibility_settings_updated_at
    BEFORE UPDATE ON accessibility_settings
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_learning_preferences_updated_at
    BEFORE UPDATE ON learning_preferences
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ──────────────────────────────────────────────
-- ROW LEVEL SECURITY
-- NOTE: These policies require Supabase Auth (auth.uid() function)
-- If using service role key (supabase_admin), RLS is bypassed
-- Comment out this section if not using Supabase Auth
-- ──────────────────────────────────────────────
ALTER TABLE users                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_settings       ENABLE ROW LEVEL SECURITY;
ALTER TABLE accessibility_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_preferences   ENABLE ROW LEVEL SECURITY;

-- Only create policies if auth.uid() function is available
DO $$
BEGIN
    -- Check if auth schema and auth.uid() exist
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'auth' AND p.proname = 'uid'
    ) THEN
        -- Policies using auth_user_id column for Supabase Auth integration
        CREATE POLICY "own_user_profile"
            ON users FOR ALL USING (auth.uid() = auth_user_id);

        CREATE POLICY "own_support_settings"
            ON support_settings FOR ALL
            USING (auth.uid() = (SELECT auth_user_id FROM users WHERE user_id = support_settings.user_id));

        CREATE POLICY "own_accessibility_settings"
            ON accessibility_settings FOR ALL
            USING (auth.uid() = (SELECT auth_user_id FROM users WHERE user_id = accessibility_settings.user_id));

        CREATE POLICY "own_learning_preferences"
            ON learning_preferences FOR ALL
            USING (auth.uid() = (SELECT auth_user_id FROM users WHERE user_id = learning_preferences.user_id));
    ELSE
        -- No auth.uid() available - policies not created
        -- Backend should use service role key which bypasses RLS
        RAISE NOTICE 'auth.uid() not found - RLS policies skipped. Use service role key for backend access.';
    END IF;
END $$;


-- ──────────────────────────────────────────────
-- INDEXES
-- ──────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_level           ON users(learning_level);
CREATE INDEX IF NOT EXISTS idx_users_auth_user       ON users(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_users_email           ON users(email);
CREATE INDEX IF NOT EXISTS idx_support_settings_user ON support_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_support_settings_mode ON support_settings(support_mode);
CREATE INDEX IF NOT EXISTS idx_accessibility_user    ON accessibility_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_prefs_user   ON learning_preferences(user_id);
