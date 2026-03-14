"""
Learner Profile Module

This module handles loading and managing learner profiles from Supabase.
It returns support mode, preferred format, and learning preferences for use
by the orchestrator and other agents.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import os


@dataclass
class AccessibilityPreferences:
    """Accessibility preferences for dyslexia and other support modes"""
    # Font Settings
    font_family: str = "OpenDyslexic"
    font_size: int = 18
    font_weight: str = "normal"

    # Spacing & Layout
    line_spacing: float = 2.0
    letter_spacing: float = 0.1
    word_spacing: float = 0.2
    paragraph_spacing: int = 24

    # Color & Contrast
    color_scheme: str = "cream_background"
    background_color: str = "#FFFEF0"
    text_color: str = "#333333"
    highlight_color: str = "#FFFF99"

    # Text Preferences
    text_chunking: str = "short_sentences"
    simplified_language: bool = True
    avoid_complex_words: bool = True
    max_sentence_length: int = 15

    # Reading Aids
    use_text_to_speech: bool = False
    tts_speed: float = 1.0
    tts_voice: str = "default"
    use_reading_ruler: bool = False
    use_dyslexia_friendly_fonts: bool = True

    # Visual Aids
    enable_images: bool = True
    enable_diagrams: bool = True
    enable_videos: bool = True
    reduce_visual_clutter: bool = True

    # Interaction Preferences
    prefer_multiple_choice: bool = True
    prefer_visual_questions: bool = True
    enable_hints: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class LearningPreferences:
    """Learning style and preferences"""
    # Learning Style
    learning_style: str = "visual"  # visual, auditory, kinesthetic, mixed
    preferred_content_format: List[str] = None

    # Pacing & Difficulty
    learning_pace: str = "moderate"  # slow, moderate, fast, adaptive
    difficulty_preference: str = "adaptive"

    # Session Preferences
    preferred_session_length: int = 30  # minutes
    break_frequency: int = 15  # minutes
    daily_goal_minutes: int = 60

    # Content Preferences
    enable_gamification: bool = True
    show_progress_bars: bool = True
    enable_rewards: bool = True
    enable_leaderboards: bool = False

    # Quiz Preferences
    quiz_frequency: str = "after_each_lesson"
    quiz_difficulty: str = "adaptive"
    instant_feedback: bool = True
    show_correct_answers: bool = True

    # Notification Preferences
    email_notifications: bool = True
    reminder_notifications: bool = True
    achievement_notifications: bool = True

    def __post_init__(self):
        if self.preferred_content_format is None:
            self.preferred_content_format = ["text", "video"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MasteryLevel:
    """Mastery level for a specific topic"""
    subject: str
    topic: str
    subtopic: Optional[str] = None
    mastery_score: float = 0.0  # 0.0 to 1.0
    confidence_level: str = "low"  # low, medium, high
    lessons_completed: int = 0
    lessons_total: int = 0
    quizzes_attempted: int = 0
    quizzes_passed: int = 0
    average_quiz_score: float = 0.0
    is_struggling: bool = False
    needs_revision: bool = False
    is_mastered: bool = False
    last_practiced_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.last_practiced_at:
            data['last_practiced_at'] = self.last_practiced_at.isoformat()
        return data


@dataclass
class LearnerProfile:
    """Complete learner profile"""
    # Core Information
    user_id: str
    email: str
    full_name: str
    username: Optional[str] = None

    # Support & Accessibility
    support_mode: str = "standard"  # standard, dyslexia, adhd, visual_impairment
    disability_type: List[str] = None

    # Learning Profile
    learning_level: str = "beginner"  # beginner, intermediate, advanced
    age_group: Optional[str] = None  # child, teen, adult
    grade_level: Optional[str] = None

    # Preferences (nested objects)
    accessibility_preferences: Optional[AccessibilityPreferences] = None
    learning_preferences: Optional[LearningPreferences] = None

    # Mastery Levels (dict of topic -> MasteryLevel)
    mastery_levels: Dict[str, float] = None

    # Account Status
    is_active: bool = True
    onboarding_completed: bool = False

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    def __post_init__(self):
        if self.disability_type is None:
            self.disability_type = []
        if self.mastery_levels is None:
            self.mastery_levels = {}
        if self.accessibility_preferences is None:
            self.accessibility_preferences = AccessibilityPreferences()
        if self.learning_preferences is None:
            self.learning_preferences = LearningPreferences()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for orchestrator context"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'full_name': self.full_name,
            'username': self.username,
            'support_mode': self.support_mode,
            'disability_type': self.disability_type,
            'learning_level': self.learning_level,
            'age_group': self.age_group,
            'grade_level': self.grade_level,
            'accessibility_preferences': self.accessibility_preferences.to_dict(),
            'learning_preferences': self.learning_preferences.to_dict(),
            'mastery_levels': self.mastery_levels,
            'is_active': self.is_active,
            'onboarding_completed': self.onboarding_completed
        }

    def get_support_mode(self) -> str:
        """Returns the support mode (dyslexia, adhd, etc.)"""
        return self.support_mode

    def get_preferred_format(self) -> Dict[str, Any]:
        """Returns preferred content format and accessibility settings"""
        return {
            'content_format': self.learning_preferences.preferred_content_format,
            'font_family': self.accessibility_preferences.font_family,
            'font_size': self.accessibility_preferences.font_size,
            'line_spacing': self.accessibility_preferences.line_spacing,
            'color_scheme': self.accessibility_preferences.color_scheme,
            'text_chunking': self.accessibility_preferences.text_chunking,
            'simplified_language': self.accessibility_preferences.simplified_language,
            'use_tts': self.accessibility_preferences.use_text_to_speech
        }

    def get_learning_preferences(self) -> Dict[str, Any]:
        """Returns learning preferences"""
        return self.learning_preferences.to_dict()

    def has_disability(self, disability: str) -> bool:
        """Check if user has a specific disability"""
        return disability.lower() in [d.lower() for d in self.disability_type]

    def is_dyslexic(self) -> bool:
        """Check if user has dyslexia"""
        return self.has_disability('dyslexia')

    def get_mastery_level(self, subject: str, topic: str) -> float:
        """Get mastery level for a specific topic"""
        key = f"{subject}:{topic}"
        return self.mastery_levels.get(key, 0.0)

    def is_struggling_with(self, subject: str, topic: str) -> bool:
        """Check if user is struggling with a topic"""
        mastery = self.get_mastery_level(subject, topic)
        return mastery < 0.40


class LearnerProfileService:
    """Service for loading and managing learner profiles from Supabase"""

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize the profile service

        Args:
            supabase_url: Supabase project URL (or set SUPABASE_URL env var)
            supabase_key: Supabase anon/service key (or set SUPABASE_KEY env var)
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase credentials not provided. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables "
                "or pass them to the constructor."
            )

        # Initialize Supabase client (will be imported when needed)
        self.supabase = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        except ImportError:
            raise ImportError(
                "supabase-py is not installed. "
                "Install it with: pip install supabase"
            )

    async def load_profile(self, user_id: str) -> LearnerProfile:
        """
        Load complete learner profile from Supabase

        Args:
            user_id: User's UUID

        Returns:
            LearnerProfile object
        """
        # Load user profile
        user_response = self.supabase.table('user_profiles').select('*').eq('user_id', user_id).single().execute()

        if not user_response.data:
            raise ValueError(f"User profile not found for user_id: {user_id}")

        user_data = user_response.data

        # Load accessibility preferences
        accessibility_response = self.supabase.table('accessibility_preferences').select('*').eq('user_id', user_id).single().execute()
        accessibility_data = accessibility_response.data if accessibility_response.data else {}

        # Load learning preferences
        learning_response = self.supabase.table('learning_preferences').select('*').eq('user_id', user_id).single().execute()
        learning_data = learning_response.data if learning_response.data else {}

        # Load mastery levels
        mastery_response = self.supabase.table('mastery_levels').select('*').eq('user_id', user_id).execute()
        mastery_data = mastery_response.data if mastery_response.data else []

        # Build mastery levels dictionary
        mastery_levels = {}
        for mastery in mastery_data:
            key = f"{mastery['subject']}:{mastery['topic']}"
            mastery_levels[key] = mastery['mastery_score']

        # Construct profile
        profile = LearnerProfile(
            user_id=user_data['user_id'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            username=user_data.get('username'),
            support_mode=user_data.get('support_mode', 'standard'),
            disability_type=user_data.get('disability_type', []),
            learning_level=user_data.get('learning_level', 'beginner'),
            age_group=user_data.get('age_group'),
            grade_level=user_data.get('grade_level'),
            is_active=user_data.get('is_active', True),
            onboarding_completed=user_data.get('onboarding_completed', False),
            accessibility_preferences=AccessibilityPreferences(**{
                k: v for k, v in accessibility_data.items()
                if k in AccessibilityPreferences.__dataclass_fields__
            }) if accessibility_data else AccessibilityPreferences(),
            learning_preferences=LearningPreferences(**{
                k: v for k, v in learning_data.items()
                if k in LearningPreferences.__dataclass_fields__
            }) if learning_data else LearningPreferences(),
            mastery_levels=mastery_levels
        )

        return profile

    def get_profile_sync(self, user_id: str) -> LearnerProfile:
        """
        Synchronous version of load_profile

        Args:
            user_id: User's UUID

        Returns:
            LearnerProfile object
        """
        # Load user profile
        user_response = self.supabase.table('user_profiles').select('*').eq('user_id', user_id).single().execute()

        if not user_response.data:
            raise ValueError(f"User profile not found for user_id: {user_id}")

        user_data = user_response.data

        # Load accessibility preferences
        accessibility_response = self.supabase.table('accessibility_preferences').select('*').eq('user_id', user_id).single().execute()
        accessibility_data = accessibility_response.data if accessibility_response.data else {}

        # Load learning preferences
        learning_response = self.supabase.table('learning_preferences').select('*').eq('user_id', user_id).single().execute()
        learning_data = learning_response.data if learning_response.data else {}

        # Load mastery levels
        mastery_response = self.supabase.table('mastery_levels').select('*').eq('user_id', user_id).execute()
        mastery_data = mastery_response.data if mastery_response.data else []

        # Build mastery levels dictionary
        mastery_levels = {}
        for mastery in mastery_data:
            key = f"{mastery['subject']}:{mastery['topic']}"
            mastery_levels[key] = mastery['mastery_score']

        # Construct profile
        profile = LearnerProfile(
            user_id=user_data['user_id'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            username=user_data.get('username'),
            support_mode=user_data.get('support_mode', 'standard'),
            disability_type=user_data.get('disability_type', []),
            learning_level=user_data.get('learning_level', 'beginner'),
            age_group=user_data.get('age_group'),
            grade_level=user_data.get('grade_level'),
            is_active=user_data.get('is_active', True),
            onboarding_completed=user_data.get('onboarding_completed', False),
            accessibility_preferences=AccessibilityPreferences(**{
                k: v for k, v in accessibility_data.items()
                if k in AccessibilityPreferences.__dataclass_fields__
            }) if accessibility_data else AccessibilityPreferences(),
            learning_preferences=LearningPreferences(**{
                k: v for k, v in learning_data.items()
                if k in LearningPreferences.__dataclass_fields__
            }) if learning_data else LearningPreferences(),
            mastery_levels=mastery_levels
        )

        return profile

    async def update_mastery_level(
        self,
        user_id: str,
        subject: str,
        topic: str,
        mastery_score: float,
        **kwargs
    ) -> None:
        """
        Update mastery level for a topic

        Args:
            user_id: User's UUID
            subject: Subject name
            topic: Topic name
            mastery_score: New mastery score (0.0 to 1.0)
            **kwargs: Additional fields to update
        """
        data = {
            'user_id': user_id,
            'subject': subject,
            'topic': topic,
            'mastery_score': mastery_score,
            **kwargs
        }

        # Upsert (insert or update)
        self.supabase.table('mastery_levels').upsert(data).execute()

    async def record_quiz_attempt(
        self,
        user_id: str,
        quiz_id: str,
        score: float,
        **kwargs
    ) -> None:
        """
        Record a quiz attempt

        Args:
            user_id: User's UUID
            quiz_id: Quiz identifier
            score: Quiz score (0.0 to 100.0)
            **kwargs: Additional quiz data
        """
        data = {
            'user_id': user_id,
            'quiz_id': quiz_id,
            'score': score,
            **kwargs
        }

        self.supabase.table('quiz_attempts').insert(data).execute()

    async def get_learning_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent learning history

        Args:
            user_id: User's UUID
            limit: Number of recent sessions to retrieve

        Returns:
            List of learning sessions
        """
        response = self.supabase.table('learning_sessions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('started_at', desc=True)\
            .limit(limit)\
            .execute()

        return response.data if response.data else []

    async def get_quiz_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent quiz attempts

        Args:
            user_id: User's UUID
            limit: Number of recent quizzes to retrieve

        Returns:
            List of quiz attempts
        """
        response = self.supabase.table('quiz_attempts')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        return response.data if response.data else []


# For use as orchestrator step handler
def create_profile_handler(profile_service: LearnerProfileService):
    """
    Factory function to create a profile handler for the orchestrator

    Args:
        profile_service: Initialized LearnerProfileService

    Returns:
        Handler function for orchestrator
    """
    def load_profile_handler(context) -> dict:
        """Load user profile and update context"""
        user_id = context.request.user_id

        # Load profile
        profile = profile_service.get_profile_sync(user_id)

        # Update context
        context.user_profile = profile.to_dict()

        # Return profile data
        return profile.to_dict()

    return load_profile_handler
