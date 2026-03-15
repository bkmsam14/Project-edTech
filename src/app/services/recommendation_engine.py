"""
RecommendationEngine — rule-based engine that maps learner analytics to
next-step recommendations.

Architecture rule:
    Agents (especially the Recommendation Agent) must NOT implement
    recommendation logic themselves.  All such logic lives here.

The engine reads from AnalyticsService and applies deterministic rules
to decide whether a learner should remediate, review, or advance.
No LLM required — keeps decisions traceable and predictable.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.app.schemas.recommendation import (
    DifficultyResult,
    NextStepResult,
    RevisionItem,
    RevisionPlan,
)

logger = logging.getLogger(__name__)

# Mastery thresholds (avg_score_pct)
_REMEDIATE_BELOW = 50.0   # below this → remediate
_REVIEW_BELOW    = 75.0   # below this → review; at/above → advance


def _score_to_difficulty(avg_score_pct: float, current_level: str) -> str:
    """Map an average score percentage to a recommended difficulty label."""
    if avg_score_pct >= 85:
        return "advanced"
    if avg_score_pct >= 65:
        return "proficient"
    if avg_score_pct >= 40:
        return "developing"
    return "beginner"


def _action_from_score(avg_score_pct: float) -> str:
    if avg_score_pct < _REMEDIATE_BELOW:
        return "remediate"
    if avg_score_pct < _REVIEW_BELOW:
        return "review"
    return "advance"


class RecommendationEngine:
    """
    Produces next-step recommendations from learner analytics.

    Usage:
        from src.database.client import supabase_admin
        from src.app.services.analytics_service import AnalyticsService
        engine = RecommendationEngine(AnalyticsService(supabase_admin))
    """

    def __init__(self, analytics_service: Any) -> None:
        """
        Args:
            analytics_service: An AnalyticsService instance.
        """
        self._analytics = analytics_service

    # ------------------------------------------------------------------
    # Core recommendations
    # ------------------------------------------------------------------

    def get_next_step(
        self,
        profile: dict,
        performance: dict,
        topic: str,
    ) -> NextStepResult:
        """
        Decide the next learning action for a learner on a specific topic.

        Args:
            profile:     ProfileOut-like dict (needs "learning_level").
            performance: learner_topic_state dict for the topic (or empty dict).
            topic:       Topic ID being evaluated.

        Returns:
            NextStepResult with action, reason, and suggested settings.
        """
        avg_score = float(performance.get("avg_score_pct", 0.0))
        attempt_count = int(performance.get("attempt_count", 0))
        current_level = profile.get("learning_level", "beginner")

        action = _action_from_score(avg_score)

        if attempt_count == 0:
            action = "review"
            reason = f"No prior attempts recorded for topic '{topic}'. Start with a review session."
        elif action == "remediate":
            reason = (
                f"Average score {avg_score:.0f}% is below the remediation threshold "
                f"({_REMEDIATE_BELOW:.0f}%). Revisit foundational material."
            )
        elif action == "review":
            reason = (
                f"Average score {avg_score:.0f}% indicates partial mastery. "
                f"Review and consolidate before advancing."
            )
        else:
            reason = (
                f"Average score {avg_score:.0f}% meets the advancement threshold "
                f"({_REVIEW_BELOW:.0f}%). Ready for next difficulty level."
            )

        difficulty = _score_to_difficulty(avg_score, current_level)
        support_mode = profile.get("support_mode", "standard")

        return NextStepResult(
            action=action,
            topic=topic,
            reason=reason,
            suggested_difficulty=difficulty,
            suggested_content_type=_suggest_content_type(support_mode),
        )

    def get_next_difficulty(
        self,
        profile: dict,
        topic: str,
        score: Optional[float] = None,
    ) -> DifficultyResult:
        """
        Recommend a difficulty level for the learner's next attempt on a topic.

        Uses the latest score if provided, otherwise falls back to the
        stored avg_score_pct from the analytics service.

        Args:
            profile: ProfileOut-like dict (needs "learning_level").
            topic:   Topic ID.
            score:   Optional override score (most recent quiz score 0-100).

        Returns:
            DifficultyResult.
        """
        current_level = profile.get("learning_level", "beginner")

        # Use the provided score if given, otherwise derive from profile level
        if score is not None:
            difficulty = _score_to_difficulty(score, current_level)
            reason = f"Based on latest score {score:.0f}%."
            return DifficultyResult(
                topic=topic,
                recommended_difficulty=difficulty,
                reason=reason,
                current_avg_score=score,
            )

        # No live score — use profile level as proxy
        level_map = {
            "beginner":   "beginner",
            "developing": "developing",
            "proficient": "proficient",
            "advanced":   "advanced",
        }
        difficulty = level_map.get(current_level, "developing")
        return DifficultyResult(
            topic=topic,
            recommended_difficulty=difficulty,
            reason=f"No recent score available; defaulting to profile level '{current_level}'.",
            current_avg_score=None,
        )

    def get_revision_plan(
        self,
        tenant_id: str,
        user_id: str,
    ) -> RevisionPlan:
        """
        Build a prioritised revision plan for all weak/at-risk topics.

        Reads the learner dashboard from AnalyticsService and converts
        weak/at-risk topic lists into ordered RevisionItems.

        Args:
            tenant_id: Tenant identifier.
            user_id:   Learner identifier.

        Returns:
            RevisionPlan with ordered RevisionItems.
        """
        dashboard = self._analytics.get_learner_dashboard(tenant_id, user_id)

        items: list[RevisionItem] = []

        # High-priority: topics that are both weak AND at-risk
        high_prio = set(dashboard.weak_topics) & set(dashboard.at_risk_topics)
        for topic in sorted(high_prio):
            items.append(RevisionItem(
                topic=topic,
                action="remediate",
                priority="high",
                reason="Topic is both weak (avg < 70%) and at-risk (avg < 75%).",
            ))

        # Medium-priority: weak but not at high risk, or at-risk but not critically weak
        medium_prio = (
            (set(dashboard.weak_topics) | set(dashboard.at_risk_topics)) - high_prio
        )
        for topic in sorted(medium_prio):
            items.append(RevisionItem(
                topic=topic,
                action="review",
                priority="medium",
                reason="Topic needs attention but is not critically failing.",
            ))

        return RevisionPlan(
            user_id=user_id,
            tenant_id=tenant_id,
            items=items,
            total_topics=len(items),
        )


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _suggest_content_type(support_mode: str) -> Optional[str]:
    """Map a support mode to a preferred content type."""
    mapping = {
        "dyslexia":          "audio",
        "visual_impairment": "audio",
        "adhd":              "visual",
        "hearing_impairment": "text",
    }
    return mapping.get(support_mode)
