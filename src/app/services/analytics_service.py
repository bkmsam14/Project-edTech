"""
AnalyticsService — single entry point for all analytics reads and writes.

Architecture rule:
    Agents MUST NOT query Supabase directly.
    All analytics access goes through this service (or the MCP wrappers that
    call it).

Constructor accepts a supabase-py Client so it can be injected with the
shared admin client from src/database/client.py or replaced with a mock
in tests.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from src.app.schemas.analytics import (
    LearnerDashboard,
    LearnerTopicState,
    QuizAnswerCreate,
    QuizAttemptCreate,
    RecommendationCreate,
)

logger = logging.getLogger(__name__)


def _now_utc() -> str:
    """Return current UTC timestamp as ISO string (Supabase-compatible)."""
    return datetime.now(timezone.utc).isoformat()


def _weakness_level(avg_score_pct: float) -> str:
    if avg_score_pct < 40:
        return "high"
    if avg_score_pct < 70:
        return "medium"
    return "low"


def _risk_level(avg_score_pct: float) -> str:
    if avg_score_pct < 50:
        return "high"
    if avg_score_pct < 75:
        return "medium"
    return "low"


class AnalyticsService:
    """
    Wraps all Supabase interactions for the analytics tables.

    Usage:
        from src.database.client import supabase_admin
        service = AnalyticsService(supabase_admin)
    """

    def __init__(self, client: Any) -> None:
        """
        Args:
            client: A supabase-py Client (or compatible mock).
                    Use supabase_admin for backend operations that
                    bypass RLS.
        """
        self._db = client

    # ------------------------------------------------------------------
    # Quiz Attempts
    # ------------------------------------------------------------------

    def record_quiz_attempt(self, attempt: QuizAttemptCreate) -> dict:
        """
        Insert a new quiz attempt row and return the inserted record.

        Called by the Assessment Agent after a quiz is scored.

        Args:
            attempt: QuizAttemptCreate – validated quiz submission data.

        Returns:
            The inserted row as a dict.
        """
        data = attempt.model_dump(exclude_none=True)
        response = (
            self._db.table("quiz_attempts")
            .insert(data)
            .execute()
        )
        row = response.data[0]
        logger.info(
            "quiz_attempt recorded id=%s user=%s score_pct=%s",
            row.get("id"), attempt.user_id, attempt.score_pct,
        )
        return row

    # ------------------------------------------------------------------
    # Quiz Answers
    # ------------------------------------------------------------------

    def record_quiz_answers(
        self,
        attempt_id: str,
        answers: list[QuizAnswerCreate],
    ) -> list[dict]:
        """
        Bulk-insert quiz answer rows linked to the given attempt.

        Args:
            attempt_id: UUID of the parent quiz_attempts row.
            answers:    List of QuizAnswerCreate – one per question.

        Returns:
            List of inserted rows as dicts.
        """
        if not answers:
            return []

        rows = [
            {"attempt_id": attempt_id, **a.model_dump(exclude_none=True)}
            for a in answers
        ]
        response = (
            self._db.table("quiz_answers")
            .insert(rows)
            .execute()
        )
        logger.info(
            "quiz_answers recorded attempt_id=%s count=%d",
            attempt_id, len(response.data),
        )
        return response.data

    # ------------------------------------------------------------------
    # Learner Topic State
    # ------------------------------------------------------------------

    def upsert_topic_state(
        self,
        tenant_id: str,
        user_id: str,
        course_id: Optional[str],
        topic_id: str,
        latest_score_pct: float,
    ) -> dict:
        """
        Create or update the rolling mastery/risk state for one topic.

        Logic:
        - If no row exists, create it with attempt_count=1.
        - If row exists:
            attempt_count += 1
            avg_score_pct  = rolling average
            mastery_score  = avg_score_pct / 100
            weakness_level / risk_level  recomputed from avg_score_pct

        Args:
            tenant_id:        Tenant identifier.
            user_id:          Learner identifier.
            course_id:        Optional course scoping.
            topic_id:         Topic being updated.
            latest_score_pct: Score (0-100) from the most recent attempt.

        Returns:
            The upserted row as a dict.
        """
        existing = self.get_topic_state(tenant_id, user_id, topic_id, course_id)

        now = _now_utc()

        if existing is None:
            # First attempt for this topic — create a fresh row.
            new_avg = latest_score_pct
            payload = {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "course_id": course_id,
                "topic_id": topic_id,
                "attempt_count": 1,
                "last_score_pct": latest_score_pct,
                "avg_score_pct": new_avg,
                "mastery_score": round(new_avg / 100.0, 4),
                "weakness_level": _weakness_level(new_avg),
                "risk_level": _risk_level(new_avg),
                "last_seen_at": now,
                "updated_at": now,
            }
            response = (
                self._db.table("learner_topic_state")
                .insert(payload)
                .execute()
            )
        else:
            # Subsequent attempt — update rolling values.
            old_count = existing["attempt_count"]
            old_avg = float(existing["avg_score_pct"])
            new_count = old_count + 1
            new_avg = (old_avg * old_count + latest_score_pct) / new_count

            payload = {
                "attempt_count": new_count,
                "last_score_pct": latest_score_pct,
                "avg_score_pct": round(new_avg, 4),
                "mastery_score": round(new_avg / 100.0, 4),
                "weakness_level": _weakness_level(new_avg),
                "risk_level": _risk_level(new_avg),
                "last_seen_at": now,
                "updated_at": now,
            }
            query = (
                self._db.table("learner_topic_state")
                .update(payload)
                .eq("id", existing["id"])
            )
            response = query.execute()

        row = response.data[0]
        logger.info(
            "topic_state upserted user=%s topic=%s avg=%.1f weakness=%s risk=%s",
            user_id, topic_id, row["avg_score_pct"],
            row["weakness_level"], row["risk_level"],
        )
        return row

    def get_topic_state(
        self,
        tenant_id: str,
        user_id: str,
        topic_id: str,
        course_id: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Fetch the current topic state row for a learner, or None if not found.

        Args:
            tenant_id: Tenant identifier.
            user_id:   Learner identifier.
            topic_id:  Topic identifier.
            course_id: Optional course scope.

        Returns:
            Row dict or None.
        """
        query = (
            self._db.table("learner_topic_state")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
            .eq("topic_id", topic_id)
        )
        # course_id NULL filtering: IS NULL vs equality
        if course_id is None:
            query = query.is_("course_id", "null")
        else:
            query = query.eq("course_id", course_id)

        response = query.execute()
        return response.data[0] if response.data else None

    # ------------------------------------------------------------------
    # Learner Dashboard
    # ------------------------------------------------------------------

    def get_learner_dashboard(
        self,
        tenant_id: str,
        user_id: str,
        course_id: Optional[str] = None,
    ) -> LearnerDashboard:
        """
        Build an aggregated analytics view for a learner.

        Returns all topic states, derives weak/at-risk topic lists, and
        computes a recent average score from the 10 most recent attempts.

        Args:
            tenant_id: Tenant identifier.
            user_id:   Learner identifier.
            course_id: Optional course scope for filtering.

        Returns:
            LearnerDashboard pydantic model.
        """
        # --- topic states ---
        ts_query = (
            self._db.table("learner_topic_state")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
        )
        if course_id is not None:
            ts_query = ts_query.eq("course_id", course_id)

        ts_response = ts_query.execute()
        raw_states = ts_response.data or []

        topic_states = [LearnerTopicState(**row) for row in raw_states]

        weak_topics = [
            s.topic_id
            for s in topic_states
            if s.weakness_level in ("medium", "high")
        ]
        at_risk_topics = [
            s.topic_id
            for s in topic_states
            if s.risk_level in ("medium", "high")
        ]

        # --- recent average score from latest 10 attempts ---
        attempt_query = (
            self._db.table("quiz_attempts")
            .select("score_pct")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(10)
        )
        if course_id is not None:
            attempt_query = attempt_query.eq("course_id", course_id)

        attempt_response = attempt_query.execute()
        scores = [row["score_pct"] for row in (attempt_response.data or [])]
        recent_average_score = (
            round(sum(scores) / len(scores), 2) if scores else None
        )

        return LearnerDashboard(
            tenant_id=tenant_id,
            user_id=user_id,
            weak_topics=weak_topics,
            at_risk_topics=at_risk_topics,
            topic_states=topic_states,
            recent_average_score=recent_average_score,
        )

    # ------------------------------------------------------------------
    # Additional query helpers
    # ------------------------------------------------------------------

    def get_quiz_history(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """
        Fetch recent quiz attempts for a learner, newest first.

        Args:
            tenant_id: Tenant identifier.
            user_id:   Learner identifier.
            limit:     Max rows to return (default 20).

        Returns:
            List of quiz_attempts rows as dicts.
        """
        response = (
            self._db.table("quiz_attempts")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    def get_topic_performance(
        self,
        tenant_id: str,
        user_id: str,
        topic_id: str,
    ) -> Optional[dict]:
        """
        Get the current mastery/risk row for a specific topic.

        Delegates to get_topic_state — provided as a named alias so
        callers have a semantically clear method for performance queries.

        Args:
            tenant_id: Tenant identifier.
            user_id:   Learner identifier.
            topic_id:  Topic identifier.

        Returns:
            learner_topic_state row or None.
        """
        return self.get_topic_state(tenant_id, user_id, topic_id)

    def get_recent_performance(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """
        Fetch a slim view of recent quiz attempts for performance trend analysis.

        Returns lighter rows (id, topic_id, score_pct, total_questions,
        created_at) so callers can chart trends without loading full rows.

        Args:
            tenant_id: Tenant identifier.
            user_id:   Learner identifier.
            limit:     Max rows to return (default 10).

        Returns:
            List of dicts with selected columns, newest first.
        """
        response = (
            self._db.table("quiz_attempts")
            .select("id, topic_id, score_pct, score_raw, total_questions, created_at")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def add_recommendation(self, rec: RecommendationCreate) -> dict:
        """
        Log a recommendation generated by an agent.

        Args:
            rec: RecommendationCreate – recommendation payload.

        Returns:
            The inserted row as a dict.
        """
        data = rec.model_dump(exclude_none=True)
        response = (
            self._db.table("recommendation_history")
            .insert(data)
            .execute()
        )
        row = response.data[0]
        logger.info(
            "recommendation recorded user=%s type=%s topic=%s",
            rec.user_id, rec.recommendation_type, rec.topic_id,
        )
        return row

    def get_recent_recommendations(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """
        Fetch the most recent recommendations for a learner.

        Args:
            tenant_id: Tenant identifier.
            user_id:   Learner identifier.
            limit:     Maximum rows to return (default 10).

        Returns:
            List of recommendation_history rows as dicts, newest first.
        """
        response = (
            self._db.table("recommendation_history")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
