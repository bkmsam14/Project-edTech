-- ============================================================
-- AI Educational Platform - Profile Database Migration
-- Paste this entire file into the Supabase SQL Editor and run
-- ============================================================


-- ============================================================
-- 1. CORE USER PROFILE
-- ============================================================
CREATE TABLE user_profiles (
    user_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    full_name   VARCHAR(255) NOT NULL,
    username    VARCHAR(100) UNIQUE,

    -- Support Mode
    support_mode   VARCHAR(50) DEFAULT 'standard',
    disability_type TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Learning Profile
    learning_level  VARCHAR(50) DEFAULT 'beginner',
    age_group       VARCHAR(50),
    grade_level     VARCHAR(20),

    -- Status
    is_active              BOOLEAN DEFAULT true,
    onboarding_completed   BOOLEAN DEFAULT false,

    -- Timestamps
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    updated_at     TIMESTAMPTZ DEFAULT NOW(),
    last_login_at  TIMESTAMPTZ,

    CONSTRAINT valid_support_mode CHECK (
        support_mode IN ('standard', 'dyslexia', 'adhd', 'visual_impairment', 'hearing_impairment')
    ),
    CONSTRAINT valid_learning_level CHECK (
        learning_level IN ('beginner', 'intermediate', 'advanced')
    )
);


-- ============================================================
-- 2. ACCESSIBILITY PREFERENCES
-- ============================================================
CREATE TABLE accessibility_preferences (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Font
    font_family  VARCHAR(100) DEFAULT 'OpenDyslexic',
    font_size    INTEGER      DEFAULT 18,
    font_weight  VARCHAR(20)  DEFAULT 'normal',

    -- Spacing
    line_spacing       DECIMAL(3,1) DEFAULT 2.0,
    letter_spacing     DECIMAL(3,1) DEFAULT 0.1,
    word_spacing       DECIMAL(3,1) DEFAULT 0.2,
    paragraph_spacing  INTEGER      DEFAULT 24,

    -- Colors
    color_scheme       VARCHAR(50) DEFAULT 'cream_background',
    background_color   VARCHAR(7)  DEFAULT '#FFFEF0',
    text_color         VARCHAR(7)  DEFAULT '#333333',
    highlight_color    VARCHAR(7)  DEFAULT '#FFFF99',

    -- Text
    text_chunking          VARCHAR(50) DEFAULT 'short_sentences',
    simplified_language    BOOLEAN     DEFAULT true,
    avoid_complex_words    BOOLEAN     DEFAULT true,
    max_sentence_length    INTEGER     DEFAULT 15,

    -- TTS / Reading Aids
    use_text_to_speech          BOOLEAN      DEFAULT false,
    tts_speed                   DECIMAL(3,1) DEFAULT 1.0,
    tts_voice                   VARCHAR(50)  DEFAULT 'default',
    use_reading_ruler           BOOLEAN      DEFAULT false,
    use_dyslexia_friendly_fonts BOOLEAN      DEFAULT true,

    -- Visuals
    enable_images         BOOLEAN DEFAULT true,
    enable_diagrams       BOOLEAN DEFAULT true,
    enable_videos         BOOLEAN DEFAULT true,
    reduce_visual_clutter BOOLEAN DEFAULT true,

    -- Interaction
    prefer_multiple_choice  BOOLEAN DEFAULT true,
    prefer_visual_questions BOOLEAN DEFAULT true,
    enable_hints            BOOLEAN DEFAULT true,

    -- Timestamps
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);


-- ============================================================
-- 3. LEARNING PREFERENCES
-- ============================================================
CREATE TABLE learning_preferences (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Style
    learning_style           VARCHAR(50)  DEFAULT 'visual',
    preferred_content_format TEXT[]       DEFAULT ARRAY['text', 'video'],
    learning_pace            VARCHAR(50)  DEFAULT 'moderate',
    difficulty_preference    VARCHAR(50)  DEFAULT 'adaptive',

    -- Session
    preferred_session_length  INTEGER DEFAULT 30,
    break_frequency           INTEGER DEFAULT 15,
    daily_goal_minutes        INTEGER DEFAULT 60,

    -- Engagement
    enable_gamification  BOOLEAN DEFAULT true,
    show_progress_bars   BOOLEAN DEFAULT true,
    enable_rewards       BOOLEAN DEFAULT true,
    enable_leaderboards  BOOLEAN DEFAULT false,

    -- Quiz
    quiz_frequency        VARCHAR(50) DEFAULT 'after_each_lesson',
    quiz_difficulty       VARCHAR(50) DEFAULT 'adaptive',
    instant_feedback      BOOLEAN     DEFAULT true,
    show_correct_answers  BOOLEAN     DEFAULT true,

    -- Notifications
    email_notifications        BOOLEAN DEFAULT true,
    reminder_notifications     BOOLEAN DEFAULT true,
    achievement_notifications  BOOLEAN DEFAULT true,

    -- Timestamps
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);


-- ============================================================
-- 4. MASTERY LEVELS (per topic)
-- ============================================================
CREATE TABLE mastery_levels (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Topic
    subject   VARCHAR(100) NOT NULL,
    topic     VARCHAR(200) NOT NULL,
    subtopic  VARCHAR(200),

    -- Mastery
    mastery_score     DECIMAL(3,2) DEFAULT 0.0,
    confidence_level  VARCHAR(50)  DEFAULT 'low',

    -- Progress
    lessons_completed   INTEGER      DEFAULT 0,
    lessons_total       INTEGER      DEFAULT 0,
    quizzes_attempted   INTEGER      DEFAULT 0,
    quizzes_passed      INTEGER      DEFAULT 0,
    average_quiz_score  DECIMAL(5,2) DEFAULT 0.0,
    time_spent_minutes  INTEGER      DEFAULT 0,

    -- Flags
    is_struggling    BOOLEAN DEFAULT false,
    needs_revision   BOOLEAN DEFAULT false,
    is_mastered      BOOLEAN DEFAULT false,

    -- Timestamps
    last_practiced_at  TIMESTAMPTZ,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, subject, topic, subtopic),
    CONSTRAINT valid_mastery CHECK (mastery_score >= 0 AND mastery_score <= 1)
);


-- ============================================================
-- 5. QUIZ ATTEMPTS
-- ============================================================
CREATE TABLE quiz_attempts (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Quiz Info
    quiz_id          VARCHAR(200) NOT NULL,
    lesson_id        VARCHAR(200),
    subject          VARCHAR(100),
    topic            VARCHAR(200),
    quiz_type        VARCHAR(50)  DEFAULT 'practice',
    difficulty_level VARCHAR(50)  DEFAULT 'medium',

    -- Performance
    total_questions   INTEGER      NOT NULL,
    correct_answers   INTEGER      DEFAULT 0,
    incorrect_answers INTEGER      DEFAULT 0,
    skipped_answers   INTEGER      DEFAULT 0,
    score             DECIMAL(5,2) DEFAULT 0.0,
    percentage        DECIMAL(5,2) DEFAULT 0.0,
    passed            BOOLEAN      DEFAULT false,

    -- Time
    time_taken_seconds  INTEGER,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,

    -- Knowledge Gaps
    weak_topics   TEXT[],
    strong_topics TEXT[],

    -- Detailed Answers (flexible JSON)
    answers  JSONB,

    -- Timestamp
    created_at  TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- 6. LEARNING SESSIONS
-- ============================================================
CREATE TABLE learning_sessions (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Session Info
    session_id  VARCHAR(200) UNIQUE NOT NULL,
    lesson_id   VARCHAR(200),
    subject     VARCHAR(100),
    topic       VARCHAR(200),

    -- Metrics
    duration_minutes      INTEGER      DEFAULT 0,
    activities_completed  INTEGER      DEFAULT 0,
    quizzes_taken         INTEGER      DEFAULT 0,
    questions_answered    INTEGER      DEFAULT 0,
    hints_used            INTEGER      DEFAULT 0,
    engagement_score      DECIMAL(3,2) DEFAULT 0.0,
    focus_score           DECIMAL(3,2) DEFAULT 0.0,

    -- Flexible storage
    session_data  JSONB,

    -- Timestamps
    started_at  TIMESTAMPTZ NOT NULL,
    ended_at    TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- 7. PERFORMANCE ANALYTICS (pre-aggregated)
-- ============================================================
CREATE TABLE performance_analytics (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Time Period
    period_type   VARCHAR(50) NOT NULL,   -- daily, weekly, monthly, all_time
    period_start  DATE        NOT NULL,
    period_end    DATE        NOT NULL,

    -- Metrics
    total_time_minutes   INTEGER      DEFAULT 0,
    lessons_completed    INTEGER      DEFAULT 0,
    quizzes_taken        INTEGER      DEFAULT 0,
    average_quiz_score   DECIMAL(5,2) DEFAULT 0.0,
    improvement_rate     DECIMAL(5,2) DEFAULT 0.0,
    streak_days          INTEGER      DEFAULT 0,
    longest_streak_days  INTEGER      DEFAULT 0,

    -- Risk Assessment
    at_risk          BOOLEAN     DEFAULT false,
    risk_level       VARCHAR(50) DEFAULT 'low',
    risk_factors     TEXT[],

    -- Recommendations
    recommended_topics      TEXT[],
    recommended_difficulty  VARCHAR(50),

    -- Timestamps
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, period_type, period_start, period_end)
);


-- ============================================================
-- 8. USER GOALS
-- ============================================================
CREATE TABLE user_goals (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id  UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Goal Info
    goal_type         VARCHAR(50)  NOT NULL,
    goal_title        VARCHAR(255) NOT NULL,
    goal_description  TEXT,
    target_type       VARCHAR(50)  NOT NULL,
    target_value      DECIMAL(10,2) NOT NULL,
    current_value     DECIMAL(10,2) DEFAULT 0.0,

    -- Scope
    subject   VARCHAR(100),
    topic     VARCHAR(200),
    deadline  DATE,

    -- Status
    status                VARCHAR(50)  DEFAULT 'active',
    is_completed          BOOLEAN      DEFAULT false,
    completion_percentage DECIMAL(5,2) DEFAULT 0.0,

    -- Timestamps
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    completed_at  TIMESTAMPTZ
);


-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_user_profiles_email         ON user_profiles(email);
CREATE INDEX idx_user_profiles_support_mode  ON user_profiles(support_mode);

CREATE INDEX idx_accessibility_user          ON accessibility_preferences(user_id);
CREATE INDEX idx_learning_prefs_user         ON learning_preferences(user_id);

CREATE INDEX idx_mastery_user                ON mastery_levels(user_id);
CREATE INDEX idx_mastery_subject_topic       ON mastery_levels(subject, topic);
CREATE INDEX idx_mastery_struggling          ON mastery_levels(user_id) WHERE is_struggling = true;
CREATE INDEX idx_mastery_needs_revision      ON mastery_levels(user_id) WHERE needs_revision = true;

CREATE INDEX idx_quiz_attempts_user          ON quiz_attempts(user_id);
CREATE INDEX idx_quiz_attempts_date          ON quiz_attempts(created_at DESC);
CREATE INDEX idx_quiz_attempts_lesson        ON quiz_attempts(lesson_id);

CREATE INDEX idx_learning_sessions_user      ON learning_sessions(user_id);
CREATE INDEX idx_learning_sessions_date      ON learning_sessions(started_at DESC);

CREATE INDEX idx_performance_user            ON performance_analytics(user_id);
CREATE INDEX idx_performance_at_risk         ON performance_analytics(user_id) WHERE at_risk = true;

CREATE INDEX idx_user_goals_user             ON user_goals(user_id);
CREATE INDEX idx_user_goals_active           ON user_goals(user_id) WHERE status = 'active';


-- ============================================================
-- TRIGGERS: Auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_accessibility_updated_at
    BEFORE UPDATE ON accessibility_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_learning_prefs_updated_at
    BEFORE UPDATE ON learning_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_mastery_updated_at
    BEFORE UPDATE ON mastery_levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_performance_updated_at
    BEFORE UPDATE ON performance_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_user_goals_updated_at
    BEFORE UPDATE ON user_goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ============================================================
-- TRIGGER: Auto-calculate mastery status based on score
-- ============================================================
CREATE OR REPLACE FUNCTION update_mastery_status()
RETURNS TRIGGER AS $$
BEGIN
    -- is_mastered if score >= 0.80
    NEW.is_mastered := NEW.mastery_score >= 0.80;

    -- is_struggling if score < 0.40 and tried at least 3 quizzes
    NEW.is_struggling := NEW.mastery_score < 0.40 AND NEW.quizzes_attempted >= 3;

    -- needs_revision if not practiced in 7+ days and not fully mastered
    NEW.needs_revision := (
        NEW.last_practiced_at IS NOT NULL
        AND (NOW() - NEW.last_practiced_at) > INTERVAL '7 days'
        AND NEW.mastery_score < 1.0
    );

    -- confidence_level
    NEW.confidence_level := CASE
        WHEN NEW.mastery_score >= 0.80 THEN 'high'
        WHEN NEW.mastery_score >= 0.60 THEN 'medium'
        ELSE 'low'
    END;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mastery_status
    BEFORE INSERT OR UPDATE ON mastery_levels
    FOR EACH ROW EXECUTE FUNCTION update_mastery_status();


-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE user_profiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE accessibility_preferences  ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_preferences   ENABLE ROW LEVEL SECURITY;
ALTER TABLE mastery_levels         ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts          ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_sessions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_analytics  ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_goals             ENABLE ROW LEVEL SECURITY;

-- user_profiles
CREATE POLICY "users_select_own_profile"
    ON user_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "users_update_own_profile"
    ON user_profiles FOR UPDATE USING (auth.uid() = user_id);

-- accessibility_preferences
CREATE POLICY "users_all_own_accessibility"
    ON accessibility_preferences FOR ALL USING (auth.uid() = user_id);

-- learning_preferences
CREATE POLICY "users_all_own_learning_prefs"
    ON learning_preferences FOR ALL USING (auth.uid() = user_id);

-- mastery_levels
CREATE POLICY "users_all_own_mastery"
    ON mastery_levels FOR ALL USING (auth.uid() = user_id);

-- quiz_attempts
CREATE POLICY "users_select_own_quizzes"
    ON quiz_attempts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "users_insert_own_quizzes"
    ON quiz_attempts FOR INSERT WITH CHECK (auth.uid() = user_id);

-- learning_sessions
CREATE POLICY "users_all_own_sessions"
    ON learning_sessions FOR ALL USING (auth.uid() = user_id);

-- performance_analytics
CREATE POLICY "users_select_own_analytics"
    ON performance_analytics FOR SELECT USING (auth.uid() = user_id);

-- user_goals
CREATE POLICY "users_all_own_goals"
    ON user_goals FOR ALL USING (auth.uid() = user_id);


-- ============================================================
-- SAMPLE DATA (delete if not needed)
-- ============================================================
DO $$
DECLARE
    v_user_id UUID := gen_random_uuid();
BEGIN

INSERT INTO user_profiles (
    user_id, email, full_name, support_mode,
    disability_type, learning_level, age_group, grade_level, onboarding_completed
) VALUES (
    v_user_id, 'student@example.com', 'Alex Johnson', 'dyslexia',
    ARRAY['dyslexia'], 'intermediate', 'teen', '8th', true
);

INSERT INTO accessibility_preferences (
    user_id, font_family, font_size, line_spacing,
    color_scheme, text_chunking, simplified_language,
    use_text_to_speech, use_dyslexia_friendly_fonts
) VALUES (
    v_user_id, 'OpenDyslexic', 18, 2.0,
    'cream_background', 'short_sentences', true,
    true, true
);

INSERT INTO learning_preferences (
    user_id, learning_style, preferred_content_format,
    learning_pace, preferred_session_length, enable_gamification
) VALUES (
    v_user_id, 'visual', ARRAY['video', 'interactive', 'text'],
    'moderate', 30, true
);

INSERT INTO mastery_levels (
    user_id, subject, topic, mastery_score,
    quizzes_attempted, quizzes_passed, average_quiz_score, lessons_completed
) VALUES
    (v_user_id, 'Mathematics', 'Algebra', 0.72, 5, 4, 74.0, 3),
    (v_user_id, 'Mathematics', 'Fractions', 0.45, 4, 2, 55.0, 2),
    (v_user_id, 'Science', 'Photosynthesis', 0.88, 6, 6, 91.0, 4);

END $$;
