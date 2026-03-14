# Profile Database Schema for Supabase

## Overview

This database supports:
1. **Adaptive Learning & Personalization** - Track performance, mastery levels, knowledge gaps
2. **Inclusive Learning (Dyslexia Support)** - Accessibility preferences, support modes

## Database Tables

### 1. user_profiles (Core Profile)
Main user profile table with basic information and support mode.

```sql
CREATE TABLE user_profiles (
    -- Primary Key
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- User Information
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE,

    -- Support & Accessibility
    support_mode VARCHAR(50) DEFAULT 'standard',  -- 'standard', 'dyslexia', 'adhd', 'visual_impairment'
    disability_type VARCHAR(100)[],  -- Array: ['dyslexia', 'dyscalculia']

    -- Learning Profile
    learning_level VARCHAR(50) DEFAULT 'beginner',  -- 'beginner', 'intermediate', 'advanced'
    age_group VARCHAR(50),  -- 'child', 'teen', 'adult'
    grade_level VARCHAR(20),  -- '5th', '8th', '11th', etc.

    -- Account Status
    is_active BOOLEAN DEFAULT true,
    onboarding_completed BOOLEAN DEFAULT false,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    CONSTRAINT valid_support_mode CHECK (
        support_mode IN ('standard', 'dyslexia', 'adhd', 'visual_impairment', 'hearing_impairment')
    )
);

-- Indexes for performance
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_support_mode ON user_profiles(support_mode);
CREATE INDEX idx_user_profiles_learning_level ON user_profiles(learning_level);
```

### 2. accessibility_preferences (Dyslexia & Accessibility Settings)
Detailed accessibility preferences for each user.

```sql
CREATE TABLE accessibility_preferences (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Font Settings
    font_family VARCHAR(100) DEFAULT 'OpenDyslexic',  -- 'OpenDyslexic', 'Comic Sans', 'Arial'
    font_size INTEGER DEFAULT 18,  -- 14, 16, 18, 20, 24
    font_weight VARCHAR(20) DEFAULT 'normal',  -- 'normal', 'bold'

    -- Spacing & Layout
    line_spacing DECIMAL(3,1) DEFAULT 2.0,  -- 1.0, 1.5, 2.0, 2.5
    letter_spacing DECIMAL(3,1) DEFAULT 0.1,  -- 0.0, 0.1, 0.2
    word_spacing DECIMAL(3,1) DEFAULT 0.2,  -- 0.0, 0.2, 0.4
    paragraph_spacing INTEGER DEFAULT 24,  -- pixels

    -- Color & Contrast
    color_scheme VARCHAR(50) DEFAULT 'cream_background',  -- 'cream_background', 'high_contrast', 'dark_mode'
    background_color VARCHAR(7) DEFAULT '#FFFEF0',  -- Hex color
    text_color VARCHAR(7) DEFAULT '#333333',
    highlight_color VARCHAR(7) DEFAULT '#FFFF99',

    -- Text Preferences
    text_chunking VARCHAR(50) DEFAULT 'short_sentences',  -- 'none', 'short_sentences', 'paragraph_breaks'
    simplified_language BOOLEAN DEFAULT true,
    avoid_complex_words BOOLEAN DEFAULT true,
    max_sentence_length INTEGER DEFAULT 15,  -- words

    -- Reading Aids
    use_text_to_speech BOOLEAN DEFAULT false,
    tts_speed DECIMAL(3,1) DEFAULT 1.0,  -- 0.5, 0.75, 1.0, 1.25, 1.5
    tts_voice VARCHAR(50) DEFAULT 'default',
    use_reading_ruler BOOLEAN DEFAULT false,
    use_dyslexia_friendly_fonts BOOLEAN DEFAULT true,

    -- Visual Aids
    enable_images BOOLEAN DEFAULT true,
    enable_diagrams BOOLEAN DEFAULT true,
    enable_videos BOOLEAN DEFAULT true,
    reduce_visual_clutter BOOLEAN DEFAULT true,

    -- Interaction Preferences
    prefer_multiple_choice BOOLEAN DEFAULT true,  -- Over text input
    prefer_visual_questions BOOLEAN DEFAULT true,
    enable_hints BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(user_id)
);

-- Index
CREATE INDEX idx_accessibility_user ON accessibility_preferences(user_id);
```

### 3. learning_preferences (Learning Style & Preferences)
How the student prefers to learn (separate from accessibility).

```sql
CREATE TABLE learning_preferences (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Learning Style
    learning_style VARCHAR(50) DEFAULT 'visual',  -- 'visual', 'auditory', 'kinesthetic', 'mixed'
    preferred_content_format VARCHAR(50)[] DEFAULT ARRAY['text', 'video'],  -- ['text', 'video', 'audio', 'interactive']

    -- Pacing & Difficulty
    learning_pace VARCHAR(50) DEFAULT 'moderate',  -- 'slow', 'moderate', 'fast', 'adaptive'
    difficulty_preference VARCHAR(50) DEFAULT 'adaptive',  -- 'easy', 'moderate', 'challenging', 'adaptive'

    -- Session Preferences
    preferred_session_length INTEGER DEFAULT 30,  -- minutes
    break_frequency INTEGER DEFAULT 15,  -- minutes before break reminder
    daily_goal_minutes INTEGER DEFAULT 60,

    -- Content Preferences
    enable_gamification BOOLEAN DEFAULT true,
    show_progress_bars BOOLEAN DEFAULT true,
    enable_rewards BOOLEAN DEFAULT true,
    enable_leaderboards BOOLEAN DEFAULT false,

    -- Quiz Preferences
    quiz_frequency VARCHAR(50) DEFAULT 'after_each_lesson',  -- 'after_each_lesson', 'daily', 'weekly'
    quiz_difficulty VARCHAR(50) DEFAULT 'adaptive',
    instant_feedback BOOLEAN DEFAULT true,
    show_correct_answers BOOLEAN DEFAULT true,

    -- Notification Preferences
    email_notifications BOOLEAN DEFAULT true,
    reminder_notifications BOOLEAN DEFAULT true,
    achievement_notifications BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(user_id)
);

-- Index
CREATE INDEX idx_learning_preferences_user ON learning_preferences(user_id);
```

### 4. mastery_levels (Topic/Subject Mastery Tracking)
Tracks student mastery for each topic/subject.

```sql
CREATE TABLE mastery_levels (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Topic Information
    subject VARCHAR(100) NOT NULL,  -- 'Mathematics', 'Science', 'Language Arts'
    topic VARCHAR(200) NOT NULL,  -- 'Algebra', 'Photosynthesis', 'Grammar'
    subtopic VARCHAR(200),  -- 'Linear Equations', 'Light Reactions'

    -- Mastery Level
    mastery_score DECIMAL(3,2) DEFAULT 0.0,  -- 0.00 to 1.00 (0% to 100%)
    confidence_level VARCHAR(50) DEFAULT 'low',  -- 'low', 'medium', 'high'

    -- Progress Tracking
    lessons_completed INTEGER DEFAULT 0,
    lessons_total INTEGER DEFAULT 0,
    quizzes_attempted INTEGER DEFAULT 0,
    quizzes_passed INTEGER DEFAULT 0,
    average_quiz_score DECIMAL(5,2) DEFAULT 0.0,  -- 0.00 to 100.00

    -- Performance Metrics
    first_attempt_success_rate DECIMAL(3,2) DEFAULT 0.0,  -- 0.00 to 1.00
    time_spent_minutes INTEGER DEFAULT 0,
    last_practiced_at TIMESTAMP WITH TIME ZONE,

    -- Status
    is_struggling BOOLEAN DEFAULT false,  -- Flagged if performance is poor
    needs_revision BOOLEAN DEFAULT false,
    is_mastered BOOLEAN DEFAULT false,  -- Mastery score >= 0.80

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(user_id, subject, topic, subtopic),
    CONSTRAINT valid_mastery_score CHECK (mastery_score >= 0.0 AND mastery_score <= 1.0)
);

-- Indexes
CREATE INDEX idx_mastery_user ON mastery_levels(user_id);
CREATE INDEX idx_mastery_subject_topic ON mastery_levels(subject, topic);
CREATE INDEX idx_mastery_struggling ON mastery_levels(is_struggling) WHERE is_struggling = true;
CREATE INDEX idx_mastery_needs_revision ON mastery_levels(needs_revision) WHERE needs_revision = true;
```

### 5. quiz_attempts (Quiz History for Analytics)
Detailed quiz attempt history for performance tracking.

```sql
CREATE TABLE quiz_attempts (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Quiz Information
    quiz_id VARCHAR(200) NOT NULL,
    lesson_id VARCHAR(200),
    subject VARCHAR(100),
    topic VARCHAR(200),

    -- Quiz Details
    quiz_type VARCHAR(50) DEFAULT 'practice',  -- 'practice', 'assessment', 'adaptive'
    difficulty_level VARCHAR(50) DEFAULT 'medium',  -- 'easy', 'medium', 'hard'
    total_questions INTEGER NOT NULL,

    -- Performance
    correct_answers INTEGER DEFAULT 0,
    incorrect_answers INTEGER DEFAULT 0,
    skipped_answers INTEGER DEFAULT 0,
    score DECIMAL(5,2) DEFAULT 0.0,  -- 0.00 to 100.00
    percentage DECIMAL(5,2) DEFAULT 0.0,  -- 0.00 to 100.00
    passed BOOLEAN DEFAULT false,

    -- Time Metrics
    time_taken_seconds INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Knowledge Gaps (detected weak topics)
    weak_topics VARCHAR(200)[],
    strong_topics VARCHAR(200)[],

    -- Answers (JSONB for flexibility)
    answers JSONB,  -- [{question_id, user_answer, correct_answer, is_correct}]

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_quiz_attempts_user ON quiz_attempts(user_id);
CREATE INDEX idx_quiz_attempts_lesson ON quiz_attempts(lesson_id);
CREATE INDEX idx_quiz_attempts_date ON quiz_attempts(created_at DESC);
CREATE INDEX idx_quiz_attempts_subject_topic ON quiz_attempts(subject, topic);
```

### 6. learning_sessions (Session Tracking)
Tracks individual learning sessions for analytics.

```sql
CREATE TABLE learning_sessions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Session Information
    session_id VARCHAR(200) UNIQUE NOT NULL,
    lesson_id VARCHAR(200),
    subject VARCHAR(100),
    topic VARCHAR(200),

    -- Session Metrics
    duration_minutes INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,

    -- Activity Tracking
    activities_completed INTEGER DEFAULT 0,
    quizzes_taken INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,

    -- Engagement Metrics
    engagement_score DECIMAL(3,2) DEFAULT 0.0,  -- 0.00 to 1.00
    focus_score DECIMAL(3,2) DEFAULT 0.0,  -- Based on time spent, interactions

    -- Session Data (JSONB)
    session_data JSONB,  -- Flexible storage for session details

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_learning_sessions_user ON learning_sessions(user_id);
CREATE INDEX idx_learning_sessions_date ON learning_sessions(started_at DESC);
CREATE INDEX idx_learning_sessions_lesson ON learning_sessions(lesson_id);
```

### 7. performance_analytics (Aggregated Analytics)
Pre-computed analytics for faster dashboard loading.

```sql
CREATE TABLE performance_analytics (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Time Period
    period_type VARCHAR(50) NOT NULL,  -- 'daily', 'weekly', 'monthly', 'all_time'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Learning Metrics
    total_time_minutes INTEGER DEFAULT 0,
    lessons_completed INTEGER DEFAULT 0,
    quizzes_taken INTEGER DEFAULT 0,
    average_quiz_score DECIMAL(5,2) DEFAULT 0.0,

    -- Performance Trends
    improvement_rate DECIMAL(5,2) DEFAULT 0.0,  -- % improvement
    streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,

    -- Risk Assessment
    at_risk BOOLEAN DEFAULT false,  -- Flagged if performance declining
    risk_level VARCHAR(50) DEFAULT 'low',  -- 'low', 'medium', 'high'
    risk_factors VARCHAR(200)[],  -- ['low_engagement', 'declining_scores']

    -- Recommendations
    recommended_topics VARCHAR(200)[],
    recommended_difficulty VARCHAR(50),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(user_id, period_type, period_start, period_end)
);

-- Indexes
CREATE INDEX idx_performance_analytics_user ON performance_analytics(user_id);
CREATE INDEX idx_performance_analytics_period ON performance_analytics(period_type, period_start);
CREATE INDEX idx_performance_analytics_at_risk ON performance_analytics(at_risk) WHERE at_risk = true;
```

### 8. user_goals (Learning Goals)
User-defined or system-recommended goals.

```sql
CREATE TABLE user_goals (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Goal Information
    goal_type VARCHAR(50) NOT NULL,  -- 'mastery', 'completion', 'time', 'streak'
    goal_title VARCHAR(255) NOT NULL,
    goal_description TEXT,

    -- Goal Target
    target_type VARCHAR(50) NOT NULL,  -- 'topic_mastery', 'quiz_score', 'daily_time'
    target_value DECIMAL(10,2) NOT NULL,
    current_value DECIMAL(10,2) DEFAULT 0.0,

    -- Goal Parameters
    subject VARCHAR(100),
    topic VARCHAR(200),
    deadline DATE,

    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'completed', 'abandoned', 'expired'
    is_completed BOOLEAN DEFAULT false,
    completion_percentage DECIMAL(5,2) DEFAULT 0.0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_user_goals_user ON user_goals(user_id);
CREATE INDEX idx_user_goals_status ON user_goals(status);
CREATE INDEX idx_user_goals_deadline ON user_goals(deadline) WHERE status = 'active';
```

## Database Functions & Triggers

### Auto-update timestamp trigger
```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accessibility_preferences_updated_at
    BEFORE UPDATE ON accessibility_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_preferences_updated_at
    BEFORE UPDATE ON learning_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mastery_levels_updated_at
    BEFORE UPDATE ON mastery_levels
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Auto-calculate mastery status
```sql
-- Function to auto-update mastery status based on score
CREATE OR REPLACE FUNCTION update_mastery_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update is_mastered flag
    NEW.is_mastered := NEW.mastery_score >= 0.80;

    -- Update is_struggling flag
    NEW.is_struggling := NEW.mastery_score < 0.40 AND NEW.quizzes_attempted >= 3;

    -- Update needs_revision flag
    NEW.needs_revision := (
        (NOW() - NEW.last_practiced_at) > INTERVAL '7 days'
        AND NEW.mastery_score < 1.0
    );

    -- Update confidence level
    IF NEW.mastery_score >= 0.80 THEN
        NEW.confidence_level := 'high';
    ELSIF NEW.mastery_score >= 0.60 THEN
        NEW.confidence_level := 'medium';
    ELSE
        NEW.confidence_level := 'low';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_update_mastery_status
    BEFORE INSERT OR UPDATE ON mastery_levels
    FOR EACH ROW
    EXECUTE FUNCTION update_mastery_status();
```

## Row Level Security (RLS) Policies

### Enable RLS on all tables
```sql
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE accessibility_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE mastery_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_goals ENABLE ROW LEVEL SECURITY;
```

### RLS Policies (users can only access their own data)
```sql
-- user_profiles
CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = user_id);

-- accessibility_preferences
CREATE POLICY "Users can view own accessibility preferences"
    ON accessibility_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own accessibility preferences"
    ON accessibility_preferences FOR ALL
    USING (auth.uid() = user_id);

-- learning_preferences
CREATE POLICY "Users can view own learning preferences"
    ON learning_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own learning preferences"
    ON learning_preferences FOR ALL
    USING (auth.uid() = user_id);

-- mastery_levels
CREATE POLICY "Users can view own mastery levels"
    ON mastery_levels FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can update mastery levels"
    ON mastery_levels FOR ALL
    USING (auth.uid() = user_id);

-- quiz_attempts
CREATE POLICY "Users can view own quiz attempts"
    ON quiz_attempts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own quiz attempts"
    ON quiz_attempts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- learning_sessions
CREATE POLICY "Users can view own learning sessions"
    ON learning_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own sessions"
    ON learning_sessions FOR ALL
    USING (auth.uid() = user_id);

-- performance_analytics
CREATE POLICY "Users can view own analytics"
    ON performance_analytics FOR SELECT
    USING (auth.uid() = user_id);

-- user_goals
CREATE POLICY "Users can manage own goals"
    ON user_goals FOR ALL
    USING (auth.uid() = user_id);
```

## Sample Data for Testing

```sql
-- Insert sample user
INSERT INTO user_profiles (
    user_id,
    email,
    full_name,
    support_mode,
    disability_type,
    learning_level,
    age_group,
    grade_level
) VALUES (
    gen_random_uuid(),
    'student@example.com',
    'Alex Johnson',
    'dyslexia',
    ARRAY['dyslexia'],
    'intermediate',
    'teen',
    '8th'
);

-- Insert accessibility preferences for dyslexic student
INSERT INTO accessibility_preferences (
    user_id,
    font_family,
    font_size,
    line_spacing,
    color_scheme,
    text_chunking,
    simplified_language,
    use_text_to_speech
) VALUES (
    (SELECT user_id FROM user_profiles WHERE email = 'student@example.com'),
    'OpenDyslexic',
    18,
    2.0,
    'cream_background',
    'short_sentences',
    true,
    true
);

-- Insert learning preferences
INSERT INTO learning_preferences (
    user_id,
    learning_style,
    preferred_content_format,
    learning_pace,
    preferred_session_length,
    enable_gamification
) VALUES (
    (SELECT user_id FROM user_profiles WHERE email = 'student@example.com'),
    'visual',
    ARRAY['video', 'interactive', 'text'],
    'moderate',
    30,
    true
);
```

## Next Steps

1. **Create these tables in Supabase** using the SQL editor
2. **Set up RLS policies** for security
3. **Create indexes** for performance
4. **Add triggers** for auto-updates
5. **Test with sample data**
6. **Connect to your orchestrator** via step handlers
