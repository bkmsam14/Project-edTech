-- ============================================================
-- ANALYTICS DB
-- Supabase / PostgreSQL
--
-- Contains:
--   1. mastery_levels       → per-topic mastery scores per student
--   2. quiz_attempts        → every quiz taken + answers
--   3. quiz_questions       → individual question results per attempt
--   4. learning_sessions    → time-on-task per session
--   5. performance_summary  → aggregated weekly/monthly stats
--   6. risk_flags           → academic risk detection
--
-- Used by:
--   → Assessment Agent     (writes mastery, quiz results, risk flags)
--   → Recommendation Agent (reads mastery, risk flags, history)
--   → Orchestrator         (reads history for RECOMMEND_NEXT workflow)
-- ============================================================


-- ──────────────────────────────────────────────
-- TABLE 1: mastery_levels
-- One row per (student, subject, topic).
-- Updated by the Assessment Agent after every quiz.
-- Read by the Recommendation Agent to suggest next steps.
-- ──────────────────────────────────────────────
CREATE TABLE mastery_levels (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Topic Coordinates
    subject                 TEXT NOT NULL,   -- e.g. 'Mathematics'
    topic                   TEXT NOT NULL,   -- e.g.  'Algebra'
    subtopic                TEXT,            -- e.g.  'Linear Equations' (nullable)

    -- Mastery Score  [0.00 – 1.00]
    mastery_score           NUMERIC(4,3) DEFAULT 0.0
                            CHECK (mastery_score BETWEEN 0.0 AND 1.0),

    -- Computed status columns (kept in sync by trigger below)
    is_mastered             BOOLEAN DEFAULT FALSE,   -- score >= 0.80
    is_struggling           BOOLEAN DEFAULT FALSE,   -- score < 0.40 after ≥3 attempts
    needs_revision          BOOLEAN DEFAULT FALSE,   -- not practiced in > 7 days

    -- Counters
    lessons_completed       INT DEFAULT 0,
    quizzes_attempted       INT DEFAULT 0,
    quizzes_passed          INT DEFAULT 0,           -- score >= 60%
    avg_quiz_score          NUMERIC(5,2) DEFAULT 0,  -- 0–100

    -- Time
    time_spent_minutes      INT DEFAULT 0,
    first_studied_at        TIMESTAMPTZ DEFAULT NOW(),
    last_practiced_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE (user_id, subject, topic, subtopic)
);

COMMENT ON TABLE mastery_levels IS
    'Tracks per-topic mastery for each student.
     Written by Assessment Agent, read by Recommendation Agent.';


-- Trigger: auto-compute status flags after every update
CREATE OR REPLACE FUNCTION compute_mastery_flags()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.is_mastered   := NEW.mastery_score >= 0.80;
    NEW.is_struggling := NEW.mastery_score < 0.40 AND NEW.quizzes_attempted >= 3;
    NEW.needs_revision := (
        NEW.mastery_score < 1.0
        AND NEW.last_practiced_at < NOW() - INTERVAL '7 days'
    );
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_mastery_flags
    BEFORE INSERT OR UPDATE ON mastery_levels
    FOR EACH ROW EXECUTE FUNCTION compute_mastery_flags();

CREATE INDEX idx_mastery_user            ON mastery_levels(user_id);
CREATE INDEX idx_mastery_subject_topic   ON mastery_levels(subject, topic);
CREATE INDEX idx_mastery_struggling      ON mastery_levels(user_id) WHERE is_struggling = TRUE;
CREATE INDEX idx_mastery_needs_revision  ON mastery_levels(user_id) WHERE needs_revision = TRUE;


-- ──────────────────────────────────────────────
-- TABLE 2: quiz_attempts
-- One row per quiz session.
-- Written by Assessment Agent.
-- ──────────────────────────────────────────────
CREATE TABLE quiz_attempts (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Context
    quiz_id           TEXT NOT NULL,
    lesson_id         TEXT,
    subject           TEXT,
    topic             TEXT,

    -- Quiz Meta
    quiz_type         TEXT DEFAULT 'practice'
                      CHECK (quiz_type IN ('practice', 'assessment', 'adaptive', 'revision')),
    difficulty        TEXT DEFAULT 'medium'
                      CHECK (difficulty IN ('easy', 'medium', 'hard', 'adaptive')),
    total_questions   INT NOT NULL,

    -- Scores
    correct_count     INT DEFAULT 0,
    incorrect_count   INT DEFAULT 0,
    skipped_count     INT DEFAULT 0,
    score_pct         NUMERIC(5,2) DEFAULT 0.0 CHECK (score_pct BETWEEN 0 AND 100),
    passed            BOOLEAN DEFAULT FALSE,   -- score_pct >= 60

    -- Timing
    started_at        TIMESTAMPTZ,
    completed_at      TIMESTAMPTZ,
    duration_seconds  INT,

    -- Knowledge Gaps (computed by Assessment Agent)
    weak_topics       TEXT[],    -- topics the student got wrong
    strong_topics     TEXT[],    -- topics the student got right

    created_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE quiz_attempts IS
    'Records every quiz attempt. weak_topics drives Recommendation Agent logic.';

CREATE INDEX idx_quiz_user        ON quiz_attempts(user_id);
CREATE INDEX idx_quiz_lesson      ON quiz_attempts(lesson_id);
CREATE INDEX idx_quiz_created     ON quiz_attempts(created_at DESC);
CREATE INDEX idx_quiz_topic       ON quiz_attempts(subject, topic);


-- ──────────────────────────────────────────────
-- TABLE 3: quiz_questions
-- One row per question per attempt.
-- Granular data used for knowledge gap detection.
-- ──────────────────────────────────────────────
CREATE TABLE quiz_questions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id      UUID NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Question
    question_id     TEXT NOT NULL,
    question_text   TEXT,
    question_type   TEXT CHECK (question_type IN (
                        'multiple_choice', 'true_false',
                        'short_answer', 'fill_blank'
                    )),
    topic_tag       TEXT,     -- which micro-topic this question tests

    -- Answers
    correct_answer  TEXT,
    user_answer     TEXT,
    is_correct      BOOLEAN DEFAULT FALSE,

    -- Timing
    time_taken_seconds INT,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE quiz_questions IS
    'Per-question results for each quiz attempt.
     Enables fine-grained knowledge gap detection.';

CREATE INDEX idx_qq_attempt   ON quiz_questions(attempt_id);
CREATE INDEX idx_qq_user      ON quiz_questions(user_id);
CREATE INDEX idx_qq_topic_tag ON quiz_questions(topic_tag);
CREATE INDEX idx_qq_incorrect ON quiz_questions(user_id) WHERE is_correct = FALSE;


-- ──────────────────────────────────────────────
-- TABLE 4: learning_sessions
-- One row per user session.
-- Tracks time-on-task per lesson / topic.
-- ──────────────────────────────────────────────
CREATE TABLE learning_sessions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Context (matches OrchestratorRequest.session_id)
    session_id       TEXT UNIQUE NOT NULL,
    lesson_id        TEXT,
    subject          TEXT,
    topic            TEXT,

    -- Time
    started_at       TIMESTAMPTZ NOT NULL,
    ended_at         TIMESTAMPTZ,
    duration_minutes INT DEFAULT 0,

    -- Activity Counts
    intents_handled     INT DEFAULT 0,   -- how many orchestrator requests in this session
    quizzes_taken       INT DEFAULT 0,
    hints_used          INT DEFAULT 0,
    tts_used            BOOLEAN DEFAULT FALSE,

    -- Engagement [0.00 – 1.00]
    engagement_score    NUMERIC(3,2) DEFAULT 0.0,

    created_at          TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE learning_sessions IS
    'Tracks per-session activity. session_id matches OrchestratorRequest.session_id.';

CREATE INDEX idx_sessions_user    ON learning_sessions(user_id);
CREATE INDEX idx_sessions_lesson  ON learning_sessions(lesson_id);
CREATE INDEX idx_sessions_date    ON learning_sessions(started_at DESC);


-- ──────────────────────────────────────────────
-- TABLE 5: performance_summary
-- Pre-aggregated weekly/monthly stats per student.
-- Updated by a scheduled job or database function.
-- Read by the Recommendation Agent and dashboard.
-- ──────────────────────────────────────────────
CREATE TABLE performance_summary (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    period_type           TEXT NOT NULL
                          CHECK (period_type IN ('weekly', 'monthly', 'all_time')),
    period_start          DATE NOT NULL,
    period_end            DATE NOT NULL,

    -- Volume
    total_time_minutes    INT DEFAULT 0,
    lessons_completed     INT DEFAULT 0,
    quizzes_taken         INT DEFAULT 0,

    -- Performance
    avg_quiz_score        NUMERIC(5,2) DEFAULT 0.0,
    improvement_rate_pct  NUMERIC(5,2) DEFAULT 0.0,   -- % change vs previous period

    -- Streaks
    current_streak_days   INT DEFAULT 0,
    longest_streak_days   INT DEFAULT 0,

    updated_at            TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, period_type, period_start)
);

CREATE INDEX idx_perf_summary_user   ON performance_summary(user_id);
CREATE INDEX idx_perf_summary_period ON performance_summary(period_type, period_start DESC);


-- ──────────────────────────────────────────────
-- TABLE 6: risk_flags
-- Academic risk detection output.
-- Written by Assessment Agent.
-- "Predict potential academic risks such as failing a course."
-- ──────────────────────────────────────────────
CREATE TABLE risk_flags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    subject         TEXT,
    topic           TEXT,

    risk_level      TEXT NOT NULL
                    CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),

    -- What triggered this flag
    risk_factors    TEXT[],
    -- e.g. ARRAY[
    --   'low_quiz_scores',
    --   'declining_trend',
    --   'not_practiced_7_days',
    --   'struggling_3_consecutive_quizzes'
    -- ]

    -- Status
    is_resolved     BOOLEAN DEFAULT FALSE,
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT,

    flagged_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE risk_flags IS
    'Academic risk detection. Written by Assessment Agent when a student
     shows declining performance or disengagement patterns.';

CREATE INDEX idx_risk_user          ON risk_flags(user_id);
CREATE INDEX idx_risk_active        ON risk_flags(user_id) WHERE is_resolved = FALSE;
CREATE INDEX idx_risk_level         ON risk_flags(risk_level);


-- ──────────────────────────────────────────────
-- ROW LEVEL SECURITY
-- ──────────────────────────────────────────────
ALTER TABLE mastery_levels      ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts       ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_questions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_sessions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_flags          ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_mastery"           ON mastery_levels      FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_quiz_attempts"     ON quiz_attempts       FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_quiz_questions"    ON quiz_questions      FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_sessions"          ON learning_sessions   FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_perf_summary"      ON performance_summary FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_risk_flags"        ON risk_flags          FOR ALL USING (auth.uid() = user_id);
