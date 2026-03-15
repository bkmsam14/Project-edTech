"""
Recommendation MCP tools — thin wrappers exposing RecommendationEngine to agents.

Architecture rule:
    The Recommendation Agent must NOT implement recommendation logic itself.
    All recommendation decisions go through RecommendationEngine via these functions.

Singletons are wired at import time using supabase_admin + AnalyticsService.
Override _engine in tests: recommendation_tools._engine = RecommendationEngine(mock)
"""

from __future__ import annotations

from typing import Optional

from src.app.services.analytics_service import AnalyticsService
from src.app.services.recommendation_engine import RecommendationEngine
from src.database.client import supabase_admin

_engine = RecommendationEngine(AnalyticsService(supabase_admin))


def recommendation_get_next_step(
    profile: dict,
    performance: dict,
    topic: str,
) -> dict:
    """
    Decide the next learning action for a learner on a specific topic.

    Args:
        profile:     ProfileOut dict (from profile_tools.profile_get).
        performance: learner_topic_state dict (from analytics_tools.analytics_get_topic_state).
        topic:       Topic ID being evaluated.

    Returns:
        NextStepResult dict with:
          - action:                 "remediate" | "review" | "advance"
          - topic:                  topic ID
          - reason:                 human-readable explanation
          - suggested_difficulty:   recommended content difficulty
          - suggested_content_type: preferred format for the learner's support mode
    """
    return _engine.get_next_step(profile, performance, topic).model_dump()


def recommendation_get_next_difficulty(
    profile: dict,
    topic: str,
    score: Optional[float] = None,
) -> dict:
    """
    Recommend a difficulty level for the learner's next content on a topic.

    Args:
        profile: ProfileOut dict.
        topic:   Topic ID.
        score:   Most recent quiz score (0-100), if available.

    Returns:
        DifficultyResult dict with recommended_difficulty and reason.
    """
    return _engine.get_next_difficulty(profile, topic, score).model_dump()


def recommendation_get_revision_plan(
    tenant_id: str,
    user_id: str,
) -> dict:
    """
    Build a prioritised revision plan for all weak/at-risk topics.

    Reads the learner dashboard from analytics and orders topics by urgency.

    Returns:
        RevisionPlan dict with a list of RevisionItems (topic, action, priority).
    """
    return _engine.get_revision_plan(tenant_id, user_id).model_dump()
