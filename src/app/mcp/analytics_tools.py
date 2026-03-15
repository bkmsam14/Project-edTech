"""
Analytics MCP tools — thin wrappers that expose AnalyticsService to agents.

Architecture rule:
    These are the ONLY public interfaces through which agents interact with
    analytics data.  Agents must never call AnalyticsService or Supabase
    directly.

Each function:
  1. Validates / assembles input into the correct Pydantic schema.
  2. Delegates entirely to AnalyticsService.
  3. Returns a plain Python dict or list (JSON-serialisable).

The AnalyticsService instance is created once at module load using the
shared supabase_admin client.  For tests, override `_service` directly.
"""

from __future__ import annotations

from typing import Optional

from src.app.schemas.analytics import (
    LearnerDashboard,
    QuizAnswerCreate,
    QuizAttemptCreate,
    RecommendationCreate,
)
from src.app.services.analytics_service import AnalyticsService
from src.database.client import supabase_admin

# Shared service instance used by all agents at runtime.
# Replace this in tests:  analytics_tools._service = AnalyticsService(mock_client)
_service = AnalyticsService(supabase_admin)


# ------------------------------------------------------------------
# Quiz Attempts
# ------------------------------------------------------------------

def analytics_record_quiz_attempt(
    tenant_id: str,
    user_id: str,
    score_raw: float,
    score_pct: float,
    total_questions: int,
    course_id: Optional[str] = None,
    lesson_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    duration_sec: Optional[int] = None,
    support_mode: Optional[str] = None,
    preferred_format: Optional[str] = None,
) -> dict:
    """
    Record a completed quiz attempt.

    Called by the Assessment Agent immediately after scoring a quiz.

    Returns:
        The inserted quiz_attempts row.
    """
    attempt = QuizAttemptCreate(
        tenant_id=tenant_id,
        user_id=user_id,
        course_id=course_id,
        lesson_id=lesson_id,
        topic_id=topic_id,
        score_raw=score_raw,
        score_pct=score_pct,
        total_questions=total_questions,
        duration_sec=duration_sec,
        support_mode=support_mode,
        preferred_format=preferred_format,
    )
    return _service.record_quiz_attempt(attempt)


# ------------------------------------------------------------------
# Quiz Answers
# ------------------------------------------------------------------

def analytics_record_quiz_answers(
    attempt_id: str,
    answers: list[dict],
) -> list[dict]:
    """
    Record individual question answers for a quiz attempt.

    Each dict in `answers` must match the QuizAnswerCreate schema:
        tenant_id, user_id, question_id, is_correct,
        topic_id?, difficulty?, error_type?, response_time_ms?

    Args:
        attempt_id: UUID of the parent quiz_attempts row.
        answers:    List of answer dicts.

    Returns:
        List of inserted quiz_answers rows.
    """
    parsed = [QuizAnswerCreate(**a) for a in answers]
    return _service.record_quiz_answers(attempt_id, parsed)


# ------------------------------------------------------------------
# Learner Topic State
# ------------------------------------------------------------------

def analytics_upsert_topic_state(
    tenant_id: str,
    user_id: str,
    topic_id: str,
    latest_score_pct: float,
    course_id: Optional[str] = None,
) -> dict:
    """
    Create or update a learner's rolling mastery/risk state for a topic.

    Called by the Assessment Agent after every scored quiz attempt.

    Returns:
        The upserted learner_topic_state row.
    """
    return _service.upsert_topic_state(
        tenant_id=tenant_id,
        user_id=user_id,
        course_id=course_id,
        topic_id=topic_id,
        latest_score_pct=latest_score_pct,
    )


def analytics_get_topic_state(
    tenant_id: str,
    user_id: str,
    topic_id: str,
    course_id: Optional[str] = None,
) -> Optional[dict]:
    """
    Fetch the current mastery/risk state for one learner–topic pair.

    Called by the Recommendation Agent before generating suggestions.

    Returns:
        learner_topic_state row dict, or None if no data recorded yet.
    """
    return _service.get_topic_state(
        tenant_id=tenant_id,
        user_id=user_id,
        topic_id=topic_id,
        course_id=course_id,
    )


# ------------------------------------------------------------------
# Learner Dashboard
# ------------------------------------------------------------------

def analytics_get_learner_dashboard(
    tenant_id: str,
    user_id: str,
    course_id: Optional[str] = None,
) -> dict:
    """
    Return an aggregated analytics view for a learner.

    Includes:
    - topic_states       – all recorded topic mastery rows
    - weak_topics        – topics with weakness_level medium/high
    - at_risk_topics     – topics with risk_level medium/high
    - recent_average_score – mean of last 10 quiz scores

    Called by the Recommendation Agent and UI layer.

    Returns:
        Serialised LearnerDashboard dict.
    """
    dashboard: LearnerDashboard = _service.get_learner_dashboard(
        tenant_id=tenant_id,
        user_id=user_id,
        course_id=course_id,
    )
    return dashboard.model_dump()


# ------------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------------

def analytics_add_recommendation(
    tenant_id: str,
    user_id: str,
    recommendation_type: str,
    course_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    recommended_mode: Optional[str] = None,
    reason: Optional[str] = None,
) -> dict:
    """
    Log a recommendation produced by the Recommendation Agent.

    Args:
        recommendation_type: e.g. "remediation", "advancement", "review"
        recommended_mode:    e.g. "visual", "audio", "text"
        reason:              Human-readable explanation for the recommendation.

    Returns:
        The inserted recommendation_history row.
    """
    rec = RecommendationCreate(
        tenant_id=tenant_id,
        user_id=user_id,
        course_id=course_id,
        topic_id=topic_id,
        recommendation_type=recommendation_type,
        recommended_mode=recommended_mode,
        reason=reason,
    )
    return _service.add_recommendation(rec)


def analytics_get_recent_recommendations(
    tenant_id: str,
    user_id: str,
    limit: int = 10,
) -> list[dict]:
    """
    Retrieve the most recent recommendations for a learner.

    Args:
        limit: Max number of rows to return (default 10).

    Returns:
        List of recommendation_history dicts, newest first.
    """
    return _service.get_recent_recommendations(
        tenant_id=tenant_id,
        user_id=user_id,
        limit=limit,
    )


# ------------------------------------------------------------------
# Quiz History / Performance Queries
# ------------------------------------------------------------------

def analytics_get_quiz_history(
    tenant_id: str,
    user_id: str,
    limit: int = 20,
) -> list[dict]:
    """
    Return full quiz attempt history for a learner, newest first.

    Called by the Assessment Agent or UI to display past attempt details.

    Args:
        limit: Max rows (default 20).

    Returns:
        List of quiz_attempts rows.
    """
    return _service.get_quiz_history(
        tenant_id=tenant_id,
        user_id=user_id,
        limit=limit,
    )


def analytics_get_topic_performance(
    tenant_id: str,
    user_id: str,
    topic_id: str,
) -> Optional[dict]:
    """
    Return current mastery/risk data for a single topic.

    Called by the Recommendation Agent before deciding next steps.

    Returns:
        learner_topic_state row dict, or None.
    """
    return _service.get_topic_performance(
        tenant_id=tenant_id,
        user_id=user_id,
        topic_id=topic_id,
    )


def analytics_get_recent_performance(
    tenant_id: str,
    user_id: str,
    limit: int = 10,
) -> list[dict]:
    """
    Return a slim performance trend view (score per attempt, newest first).

    Useful for charting score trends or detecting improvement/decline.

    Args:
        limit: Max rows (default 10).

    Returns:
        List of dicts: id, topic_id, score_pct, score_raw, total_questions, created_at.
    """
    return _service.get_recent_performance(
        tenant_id=tenant_id,
        user_id=user_id,
        limit=limit,
    )
