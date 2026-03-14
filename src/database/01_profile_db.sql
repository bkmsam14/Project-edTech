-- ============================================================
-- PROFILE DB
-- Supabase / PostgreSQL
--
-- Contains:
--   1. users             → core identity (extends Supabase Auth)
--   2. accessibility_settings  → dyslexia font/color/TTS preferences
--   3. learning_preferences    → pace, format, gamification
--   4. support_settings        → disability type + active support mode
--
-- The Learner Profile Module reads from ALL 4 tables and
-- assembles a single profile dict for the orchestrator context.
-- ============================================================


-- ──────────────────────────────────────────────
-- TABLE 1: users
-- Extends Supabase Auth (auth.users) with
-- educational profile data.
-- ──────────────────────────────────────────────
CREATE TABLE users (
    -- Links to Supabase Auth user
    user_id       UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Basic Info
    full_name     TEXT NOT NULL,
    username      TEXT UNIQUE,
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
    'Core student profile. Extends Supabase Auth. One row per student.';
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

    -- Support Mode (used by Orchestrator & Accessibility Agent)
    support_mode     TEXT NOT NULL DEFAULT 'standard'
                     CHECK (support_mode IN (
                         'standard',
                         'dyslexia',
                         'adhd',
                         'dyscalculia',
                         'visual_impairment',
                         'hearing_impairment'
                     )),

    -- Disabilities list (can have more than one)
    disability_types TEXT[],                       -- e.g. ARRAY['dyslexia', 'adhd']

    -- Severity (helps the Accessibility Agent calibrate adaptation intensity)
    severity         TEXT DEFAULT 'moderate'
                     CHECK (severity IN ('mild', 'moderate', 'severe')),

    -- Whether support mode is actively applied
    support_active   BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);

COMMENT ON TABLE support_settings IS
    'Stores the students disability type and active support mode.
     Read by the Orchestrator at the start of every workflow.';
COMMENT ON COLUMN support_settings.support_mode IS
    'The primary mode that drives the Accessibility Agent pipeline.';
COMMENT ON COLUMN support_settings.severity IS
    'Calibrates how aggressively the Accessibility Agent simplifies content.';


-- ──────────────────────────────────────────────
-- TABLE 3: accessibility_settings
-- All rendering and readability preferences.
-- Read by the Accessibility Agent to adapt
-- every response for the students disability.
-- ──────────────────────────────────────────────
CREATE TABLE accessibility_settings (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- ── Font ────────────────────────────────
    font_family             TEXT    DEFAULT 'OpenDyslexic',
    -- Common dyslexia-friendly fonts:
    -- 'OpenDyslexic', 'Lexie Readable', 'Arial', 'Comic Sans'
    font_size_px            INT     DEFAULT 18
                            CHECK (font_size_px BETWEEN 12 AND 36),
    bold_text               BOOLEAN DEFAULT FALSE,

    -- ── Spacing ─────────────────────────────
    line_spacing            NUMERIC(3,1) DEFAULT 2.0
                            CHECK (line_spacing BETWEEN 1.0 AND 3.0),
    letter_spacing_em       NUMERIC(3,2) DEFAULT 0.10,
    word_spacing_em         NUMERIC(3,2) DEFAULT 0.20,
    paragraph_gap_px        INT     DEFAULT 24,

    -- ── Colors ──────────────────────────────
    color_scheme            TEXT DEFAULT 'cream'
                            CHECK (color_scheme IN (
                                'cream',         -- off-white bg, dark text (most common for dyslexia)
                                'high_contrast', -- black bg, white text
                                'dark_mode',
                                'pastel_blue',
                                'standard'
                            )),
    background_color_hex    TEXT DEFAULT '#FFFEF0',
    text_color_hex          TEXT DEFAULT '#333333',
    highlight_color_hex     TEXT DEFAULT '#FFFF99',

    -- ── Text Simplification ──────────────────
    text_chunking           TEXT DEFAULT 'short_sentences'
                            CHECK (text_chunking IN (
                                'none', 'short_sentences', 'single_idea_per_line'
                            )),
    max_sentence_words      INT  DEFAULT 15,
    simplified_vocabulary   BOOLEAN DEFAULT TRUE,
    use_bullet_points       BOOLEAN DEFAULT TRUE,
    use_numbered_steps      BOOLEAN DEFAULT TRUE,

    -- ── Reading Aids ─────────────────────────
    use_tts                 BOOLEAN DEFAULT FALSE, -- Text-to-Speech
    tts_speed               NUMERIC(3,2) DEFAULT 1.0
                            CHECK (tts_speed BETWEEN 0.5 AND 2.0),
    tts_voice               TEXT DEFAULT 'default',
    reading_ruler           BOOLEAN DEFAULT FALSE, -- Highlights current line
    word_highlighting       BOOLEAN DEFAULT FALSE, -- Highlights word-by-word during TTS

    -- ── Visual Aids ──────────────────────────
    show_images             BOOLEAN DEFAULT TRUE,
    show_diagrams           BOOLEAN DEFAULT TRUE,
    reduce_visual_clutter   BOOLEAN DEFAULT TRUE,

    -- ── Interaction ──────────────────────────
    prefer_multiple_choice  BOOLEAN DEFAULT TRUE,  -- vs open-ended text input
    prefer_visual_questions BOOLEAN DEFAULT TRUE,
    show_hints              BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);

COMMENT ON TABLE accessibility_settings IS
    'All rendering preferences for the Accessibility Agent.
     Determines how text, fonts, colors, and interaction are adapted
     for a students disability type.';


-- ──────────────────────────────────────────────
-- TABLE 4: learning_preferences
-- How the student likes to learn.
-- Read by the Tutor Agent, Quiz Agent, and
-- Recommendation Agent.
-- ──────────────────────────────────────────────
CREATE TABLE learning_preferences (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                  UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- ── Learning Style ───────────────────────
    learning_style           TEXT DEFAULT 'visual'
                             CHECK (learning_style IN (
                                 'visual', 'auditory', 'reading_writing',
                                 'kinesthetic', 'mixed'
                             )),

    -- ── Preferred Content Format ─────────────
    -- What formats the student engages with best
    preferred_formats        TEXT[] DEFAULT ARRAY['text', 'visual'],
    -- Options: 'text', 'video', 'audio', 'interactive', 'visual', 'infographic'

    -- ── Explanation Style ────────────────────
    -- How the Tutor Agent should structure its answers
    explanation_style        TEXT DEFAULT 'step_by_step'
                             CHECK (explanation_style IN (
                                 'concise',       -- Short, direct answers
                                 'step_by_step',  -- Numbered steps
                                 'analogy_based', -- Real-world comparisons
                                 'example_first'  -- Show example before rule
                             )),

    -- ── Pacing ───────────────────────────────
    learning_pace            TEXT DEFAULT 'moderate'
                             CHECK (learning_pace IN ('slow', 'moderate', 'fast', 'adaptive')),
    session_length_minutes   INT  DEFAULT 30
                             CHECK (session_length_minutes BETWEEN 5 AND 120),
    break_every_minutes      INT  DEFAULT 20,     -- Remind to take a break
    daily_goal_minutes       INT  DEFAULT 60,

    -- ── Difficulty ───────────────────────────
    difficulty_preference    TEXT DEFAULT 'adaptive'
                             CHECK (difficulty_preference IN (
                                 'easy', 'moderate', 'challenging', 'adaptive'
                             )),

    -- ── Quiz Preferences ─────────────────────
    quiz_frequency           TEXT DEFAULT 'after_each_lesson'
                             CHECK (quiz_frequency IN (
                                 'after_each_lesson', 'daily', 'weekly', 'on_demand'
                             )),
    instant_feedback         BOOLEAN DEFAULT TRUE,  -- Show result right after answering
    show_correct_answers     BOOLEAN DEFAULT TRUE,
    max_questions_per_quiz   INT     DEFAULT 5,

    -- ── Motivation & Engagement ──────────────
    enable_gamification      BOOLEAN DEFAULT TRUE,
    show_progress_bars       BOOLEAN DEFAULT TRUE,
    enable_badges            BOOLEAN DEFAULT TRUE,
    enable_streaks           BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at               TIMESTAMPTZ DEFAULT NOW(),
    updated_at               TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);

COMMENT ON TABLE learning_preferences IS
    'Tracks how the student prefers to receive and interact with content.
     The Tutor Agent and Quiz Agent use this to shape their output style.';


-- ──────────────────────────────────────────────
-- AUTO-UPDATE TRIGGER
-- Keeps updated_at current on all 4 tables
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
-- Users can only read/write their own rows.
-- ──────────────────────────────────────────────
ALTER TABLE users                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_settings      ENABLE ROW LEVEL SECURITY;
ALTER TABLE accessibility_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_preferences  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_user_profile"
    ON users FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "own_support_settings"
    ON support_settings FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "own_accessibility_settings"
    ON accessibility_settings FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "own_learning_preferences"
    ON learning_preferences FOR ALL USING (auth.uid() = user_id);


-- ──────────────────────────────────────────────
-- INDEXES
-- ──────────────────────────────────────────────
CREATE INDEX idx_support_settings_mode  ON support_settings(support_mode);
CREATE INDEX idx_support_settings_user  ON support_settings(user_id);
CREATE INDEX idx_accessibility_user     ON accessibility_settings(user_id);
CREATE INDEX idx_learning_prefs_user    ON learning_preferences(user_id);
CREATE INDEX idx_users_level            ON users(learning_level);
