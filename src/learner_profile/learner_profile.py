"""
Learner Profile Module
======================
Reads a student's full profile from Supabase and returns a
structured dict that the Orchestrator puts into WorkflowContext.

The assembled profile includes:
  - identity        → from users
  - support_mode    → from support_settings
  - accessibility   → from accessibility_settings
  - preferences     → from learning_preferences

Usage (as an orchestrator step handler):
    from learner_profile import LearnerProfileModule

    profile_module = LearnerProfileModule(supabase_client)

    # Register as the LOAD_PROFILE step handler
    orchestrator.register_step_handler(
        WorkflowStep.LOAD_PROFILE,
        profile_module.load_profile
    )
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Data classes — typed containers for each sub-profile section.
# These map 1-to-1 with the Supabase tables.
# ─────────────────────────────────────────────────────────────────

@dataclass
class SupportSettings:
    """
    Maps to: support_settings table
    Tells the Orchestrator which accessibility pipeline to invoke.
    """
    support_mode: str = "standard"
    # Options: 'standard', 'dyslexia', 'adhd', 'dyscalculia',
    #          'visual_impairment', 'hearing_impairment'

    disability_types: list = field(default_factory=list)
    # e.g. ['dyslexia', 'adhd']

    severity: str = "moderate"
    # Options: 'mild', 'moderate', 'severe'
    # Used by Accessibility Agent to calibrate adaptation intensity

    support_active: bool = True


@dataclass
class AccessibilitySettings:
    """
    Maps to: accessibility_settings table
    Used by the Accessibility Agent to adapt every response.
    """
    # Font
    font_family: str = "OpenDyslexic"
    font_size_px: int = 18
    bold_text: bool = False

    # Spacing
    line_spacing: float = 2.0
    letter_spacing_em: float = 0.10
    word_spacing_em: float = 0.20
    paragraph_gap_px: int = 24

    # Colors
    color_scheme: str = "cream"
    background_color_hex: str = "#FFFEF0"
    text_color_hex: str = "#333333"
    highlight_color_hex: str = "#FFFF99"

    # Text Simplification
    text_chunking: str = "short_sentences"
    # Options: 'none', 'short_sentences', 'single_idea_per_line'
    max_sentence_words: int = 15
    simplified_vocabulary: bool = True
    use_bullet_points: bool = True
    use_numbered_steps: bool = True

    # Reading Aids
    use_tts: bool = False
    tts_speed: float = 1.0
    tts_voice: str = "default"
    reading_ruler: bool = False
    word_highlighting: bool = False

    # Visual Aids
    show_images: bool = True
    show_diagrams: bool = True
    reduce_visual_clutter: bool = True

    # Interaction
    prefer_multiple_choice: bool = True
    prefer_visual_questions: bool = True
    show_hints: bool = True


@dataclass
class LearningPreferences:
    """
    Maps to: learning_preferences table
    Used by Tutor Agent, Quiz Agent, Recommendation Agent.
    """
    # Learning Style
    learning_style: str = "visual"
    # Options: 'visual', 'auditory', 'reading_writing', 'kinesthetic', 'mixed'

    preferred_formats: list = field(default_factory=lambda: ["text", "visual"])
    # Options: 'text', 'video', 'audio', 'interactive', 'visual', 'infographic'

    # Explanation Style (used by Tutor Agent)
    explanation_style: str = "step_by_step"
    # Options: 'concise', 'step_by_step', 'analogy_based', 'example_first'

    # Pacing
    learning_pace: str = "moderate"
    session_length_minutes: int = 30
    daily_goal_minutes: int = 60

    # Difficulty
    difficulty_preference: str = "adaptive"

    # Quiz
    quiz_frequency: str = "after_each_lesson"
    instant_feedback: bool = True
    show_correct_answers: bool = True
    max_questions_per_quiz: int = 5

    # Engagement
    enable_gamification: bool = True
    show_progress_bars: bool = True
    enable_badges: bool = True
    enable_streaks: bool = True


@dataclass
class LearnerProfile:
    """
    The complete assembled profile.
    This is what gets stored in WorkflowContext.user_profile.
    Every agent in the pipeline reads from this.
    """
    # Core identity
    user_id: str = ""
    full_name: str = ""
    learning_level: str = "beginner"
    # Options: 'beginner', 'intermediate', 'advanced'
    grade_level: str = ""
    language: str = "en"

    # The three sub-profiles
    support: SupportSettings = field(default_factory=SupportSettings)
    accessibility: AccessibilitySettings = field(default_factory=AccessibilitySettings)
    preferences: LearningPreferences = field(default_factory=LearningPreferences)

    # Shortcut properties — used directly by Orchestrator routing logic
    @property
    def support_mode(self) -> str:
        return self.support.support_mode

    @property
    def use_tts(self) -> bool:
        return self.accessibility.use_tts

    @property
    def is_dyslexia_mode(self) -> bool:
        return self.support.support_mode == "dyslexia"

    def to_dict(self) -> dict:
        """
        Converts the full profile to a plain dict.
        This is what gets stored in WorkflowContext.user_profile.
        """
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "learning_level": self.learning_level,
            "grade_level": self.grade_level,
            "language": self.language,

            # Support
            "support_mode": self.support.support_mode,
            "disability_types": self.support.disability_types,
            "severity": self.support.severity,
            "support_active": self.support.support_active,

            # Accessibility (flat — agents access these directly)
            "accessibility": {
                "font_family": self.accessibility.font_family,
                "font_size_px": self.accessibility.font_size_px,
                "bold_text": self.accessibility.bold_text,
                "line_spacing": self.accessibility.line_spacing,
                "letter_spacing_em": self.accessibility.letter_spacing_em,
                "word_spacing_em": self.accessibility.word_spacing_em,
                "paragraph_gap_px": self.accessibility.paragraph_gap_px,
                "color_scheme": self.accessibility.color_scheme,
                "background_color_hex": self.accessibility.background_color_hex,
                "text_color_hex": self.accessibility.text_color_hex,
                "highlight_color_hex": self.accessibility.highlight_color_hex,
                "text_chunking": self.accessibility.text_chunking,
                "max_sentence_words": self.accessibility.max_sentence_words,
                "simplified_vocabulary": self.accessibility.simplified_vocabulary,
                "use_bullet_points": self.accessibility.use_bullet_points,
                "use_numbered_steps": self.accessibility.use_numbered_steps,
                "use_tts": self.accessibility.use_tts,
                "tts_speed": self.accessibility.tts_speed,
                "tts_voice": self.accessibility.tts_voice,
                "reading_ruler": self.accessibility.reading_ruler,
                "word_highlighting": self.accessibility.word_highlighting,
                "show_images": self.accessibility.show_images,
                "show_diagrams": self.accessibility.show_diagrams,
                "reduce_visual_clutter": self.accessibility.reduce_visual_clutter,
                "prefer_multiple_choice": self.accessibility.prefer_multiple_choice,
                "prefer_visual_questions": self.accessibility.prefer_visual_questions,
                "show_hints": self.accessibility.show_hints,
            },

            # Learning Preferences
            "preferences": {
                "learning_style": self.preferences.learning_style,
                "preferred_formats": self.preferences.preferred_formats,
                "explanation_style": self.preferences.explanation_style,
                "learning_pace": self.preferences.learning_pace,
                "session_length_minutes": self.preferences.session_length_minutes,
                "daily_goal_minutes": self.preferences.daily_goal_minutes,
                "difficulty_preference": self.preferences.difficulty_preference,
                "quiz_frequency": self.preferences.quiz_frequency,
                "instant_feedback": self.preferences.instant_feedback,
                "show_correct_answers": self.preferences.show_correct_answers,
                "max_questions_per_quiz": self.preferences.max_questions_per_quiz,
                "enable_gamification": self.preferences.enable_gamification,
                "show_progress_bars": self.preferences.show_progress_bars,
                "enable_badges": self.preferences.enable_badges,
                "enable_streaks": self.preferences.enable_streaks,
            },
        }


# ─────────────────────────────────────────────────────────────────
# LearnerProfileModule
# Connects to Supabase and assembles the full LearnerProfile.
# ─────────────────────────────────────────────────────────────────

class LearnerProfileModule:
    """
    Reads from all 4 Profile DB tables and returns a fully
    assembled LearnerProfile.

    This class acts as the LOAD_PROFILE step handler
    in the Orchestrator workflow.

    Args:
        supabase_client: An initialized supabase-py client.

    Example:
        from supabase import create_client
        from learner_profile import LearnerProfileModule

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        profile_module = LearnerProfileModule(supabase)

        orchestrator.register_step_handler(
            WorkflowStep.LOAD_PROFILE,
            profile_module.load_profile
        )
    """

    def __init__(self, supabase_client):
        self.db = supabase_client

    # ─────────────────────────────────────────────
    # Main entry point — called by the Orchestrator
    # ─────────────────────────────────────────────

    def load_profile(self, context) -> dict:
        """
        Orchestrator step handler for LOAD_PROFILE.

        Reads the user's profile from Supabase and stores it
        in WorkflowContext.user_profile.

        Returns:
            dict: The assembled profile (also stored in context).

        Raises:
            ValueError: If user is not found.
        """
        user_id = context.request.user_id
        logger.info(f"Loading profile for user: {user_id}")

        profile = self.get_profile(user_id)

        if profile is None:
            raise ValueError(f"User not found: {user_id}")

        profile_dict = profile.to_dict()
        context.user_profile = profile_dict

        logger.info(
            f"Profile loaded — support_mode={profile.support_mode}, "
            f"level={profile.learning_level}, "
            f"severity={profile.support.severity}"
        )

        return profile_dict

    # ─────────────────────────────────────────────
    # Core fetch — assembles all 4 tables
    # ─────────────────────────────────────────────

    def get_profile(self, user_id: str) -> Optional[LearnerProfile]:
        """
        Fetches and assembles the full LearnerProfile from Supabase.

        Joins data from:
          - users
          - support_settings
          - accessibility_settings
          - learning_preferences

        Returns None if the user is not found.
        """
        # Fetch from all 4 tables in parallel-style (4 small queries)
        user_row           = self._fetch_user(user_id)
        support_row        = self._fetch_support(user_id)
        accessibility_row  = self._fetch_accessibility(user_id)
        preferences_row    = self._fetch_preferences(user_id)

        if user_row is None:
            return None

        return self._assemble(
            user_row, support_row, accessibility_row, preferences_row
        )

    # ─────────────────────────────────────────────
    # Table fetchers
    # ─────────────────────────────────────────────

    def _fetch_user(self, user_id: str) -> Optional[dict]:
        """Fetch core identity from users table."""
        result = (
            self.db.table("users")
            .select("user_id, full_name, learning_level, grade_level, language")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data if result.data else None

    def _fetch_support(self, user_id: str) -> Optional[dict]:
        """Fetch support settings from support_settings table."""
        result = (
            self.db.table("support_settings")
            .select("support_mode, disability_types, severity, support_active")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data if result.data else None

    def _fetch_accessibility(self, user_id: str) -> Optional[dict]:
        """Fetch accessibility settings from accessibility_settings table."""
        result = (
            self.db.table("accessibility_settings")
            .select("*")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data if result.data else None

    def _fetch_preferences(self, user_id: str) -> Optional[dict]:
        """Fetch learning preferences from learning_preferences table."""
        result = (
            self.db.table("learning_preferences")
            .select("*")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data if result.data else None

    # ─────────────────────────────────────────────
    # Assembler — maps DB rows → typed dataclasses
    # ─────────────────────────────────────────────

    def _assemble(
        self,
        user_row: dict,
        support_row: Optional[dict],
        accessibility_row: Optional[dict],
        preferences_row: Optional[dict],
    ) -> LearnerProfile:
        """
        Assembles the four DB rows into a single LearnerProfile.
        Missing rows fall back to sensible defaults.
        """
        support = self._map_support(support_row)
        accessibility = self._map_accessibility(accessibility_row, support.support_mode)
        preferences = self._map_preferences(preferences_row)

        return LearnerProfile(
            user_id=user_row.get("user_id", ""),
            full_name=user_row.get("full_name", ""),
            learning_level=user_row.get("learning_level", "beginner"),
            grade_level=user_row.get("grade_level", ""),
            language=user_row.get("language", "en"),
            support=support,
            accessibility=accessibility,
            preferences=preferences,
        )

    def _map_support(self, row: Optional[dict]) -> SupportSettings:
        if not row:
            return SupportSettings()
        return SupportSettings(
            support_mode=row.get("support_mode", "standard"),
            disability_types=row.get("disability_types") or [],
            severity=row.get("severity", "moderate"),
            support_active=row.get("support_active", True),
        )

    def _map_accessibility(
        self, row: Optional[dict], support_mode: str
    ) -> AccessibilitySettings:
        """
        Maps DB row to AccessibilitySettings.
        If no row exists, auto-generates defaults based on support_mode.
        """
        if not row:
            return self._default_accessibility_for_mode(support_mode)

        return AccessibilitySettings(
            font_family=row.get("font_family", "OpenDyslexic"),
            font_size_px=row.get("font_size_px", 18),
            bold_text=row.get("bold_text", False),
            line_spacing=float(row.get("line_spacing", 2.0)),
            letter_spacing_em=float(row.get("letter_spacing_em", 0.10)),
            word_spacing_em=float(row.get("word_spacing_em", 0.20)),
            paragraph_gap_px=row.get("paragraph_gap_px", 24),
            color_scheme=row.get("color_scheme", "cream"),
            background_color_hex=row.get("background_color_hex", "#FFFEF0"),
            text_color_hex=row.get("text_color_hex", "#333333"),
            highlight_color_hex=row.get("highlight_color_hex", "#FFFF99"),
            text_chunking=row.get("text_chunking", "short_sentences"),
            max_sentence_words=row.get("max_sentence_words", 15),
            simplified_vocabulary=row.get("simplified_vocabulary", True),
            use_bullet_points=row.get("use_bullet_points", True),
            use_numbered_steps=row.get("use_numbered_steps", True),
            use_tts=row.get("use_tts", False),
            tts_speed=float(row.get("tts_speed", 1.0)),
            tts_voice=row.get("tts_voice", "default"),
            reading_ruler=row.get("reading_ruler", False),
            word_highlighting=row.get("word_highlighting", False),
            show_images=row.get("show_images", True),
            show_diagrams=row.get("show_diagrams", True),
            reduce_visual_clutter=row.get("reduce_visual_clutter", True),
            prefer_multiple_choice=row.get("prefer_multiple_choice", True),
            prefer_visual_questions=row.get("prefer_visual_questions", True),
            show_hints=row.get("show_hints", True),
        )

    def _map_preferences(self, row: Optional[dict]) -> LearningPreferences:
        if not row:
            return LearningPreferences()
        return LearningPreferences(
            learning_style=row.get("learning_style", "visual"),
            preferred_formats=row.get("preferred_formats") or ["text", "visual"],
            explanation_style=row.get("explanation_style", "step_by_step"),
            learning_pace=row.get("learning_pace", "moderate"),
            session_length_minutes=row.get("session_length_minutes", 30),
            daily_goal_minutes=row.get("daily_goal_minutes", 60),
            difficulty_preference=row.get("difficulty_preference", "adaptive"),
            quiz_frequency=row.get("quiz_frequency", "after_each_lesson"),
            instant_feedback=row.get("instant_feedback", True),
            show_correct_answers=row.get("show_correct_answers", True),
            max_questions_per_quiz=row.get("max_questions_per_quiz", 5),
            enable_gamification=row.get("enable_gamification", True),
            show_progress_bars=row.get("show_progress_bars", True),
            enable_badges=row.get("enable_badges", True),
            enable_streaks=row.get("enable_streaks", True),
        )

    def _default_accessibility_for_mode(self, support_mode: str) -> AccessibilitySettings:
        """
        Auto-generates reasonable accessibility defaults based on support_mode.
        Used when a student hasn't customized their settings yet.
        """
        if support_mode == "dyslexia":
            return AccessibilitySettings(
                font_family="OpenDyslexic",
                font_size_px=18,
                line_spacing=2.0,
                color_scheme="cream",
                text_chunking="short_sentences",
                max_sentence_words=15,
                simplified_vocabulary=True,
                use_bullet_points=True,
                reduce_visual_clutter=True,
                prefer_multiple_choice=True,
            )
        elif support_mode == "adhd":
            return AccessibilitySettings(
                font_family="Arial",
                font_size_px=16,
                line_spacing=1.8,
                color_scheme="standard",
                text_chunking="single_idea_per_line",
                max_sentence_words=12,
                simplified_vocabulary=True,
                use_bullet_points=True,
                reduce_visual_clutter=True,
                prefer_multiple_choice=True,
            )
        elif support_mode == "visual_impairment":
            return AccessibilitySettings(
                font_family="Arial",
                font_size_px=24,
                bold_text=True,
                line_spacing=2.5,
                color_scheme="high_contrast",
                use_tts=True,
                tts_speed=0.9,
                show_images=False,
                reduce_visual_clutter=True,
            )
        else:
            return AccessibilitySettings()   # Standard defaults

    # ─────────────────────────────────────────────
    # Update helpers — called by other agents
    # ─────────────────────────────────────────────

    def update_learning_level(self, user_id: str, new_level: str) -> None:
        """
        Called by Assessment Agent after evaluating quiz performance.
        Updates the student's overall learning level.
        """
        self.db.table("users").update(
            {"learning_level": new_level}
        ).eq("user_id", user_id).execute()
        logger.info(f"Updated learning_level to '{new_level}' for {user_id}")

    def update_support_mode(self, user_id: str, support_mode: str) -> None:
        """
        Called by the UI when a student changes their support mode.
        """
        self.db.table("support_settings").update(
            {"support_mode": support_mode}
        ).eq("user_id", user_id).execute()
        logger.info(f"Updated support_mode to '{support_mode}' for {user_id}")
