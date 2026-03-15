"""
Tests for AnalyticsService.

All Supabase calls are mocked — no real database required.
Each test focuses on a single behaviour: insertion data, upsert logic,
derivation of weak/at-risk topics, recommendation round-trip, etc.

Run with:
    pytest tests/test_analytics_service.py -v
"""

from __future__ import annotations

import sys
import os
from unittest.mock import MagicMock, call, patch
import pytest

# ---------------------------------------------------------------------------
# Path setup — allow imports from project root without installing the package
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.app.schemas.analytics import (
    LearnerTopicState,
    QuizAnswerCreate,
    QuizAttemptCreate,
    RecommendationCreate,
)
from src.app.services.analytics_service import (
    AnalyticsService,
    _risk_level,
    _weakness_level,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_client() -> MagicMock:
    """
    Build a MagicMock that mimics the supabase-py builder chain:
        client.table(...).insert(...).execute()  -> response
    The chain returns itself at every step except execute(), which returns
    a response object.  Individual tests configure response.data as needed.
    """
    client = MagicMock()
    # Make the builder chain fluent — every intermediate call returns the
    # same mock so callers can chain arbitrarily.
    builder = MagicMock()
    builder.insert.return_value = builder
    builder.update.return_value = builder
    builder.select.return_value = builder
    builder.upsert.return_value = builder
    builder.eq.return_value = builder
    builder.is_.return_value = builder
    builder.order.return_value = builder
    builder.limit.return_value = builder
    client.table.return_value = builder
    return client, builder


def _make_response(data: list) -> MagicMock:
    """Wrap data in a mock response object (mimics APIResponse)."""
    resp = MagicMock()
    resp.data = data
    return resp


# ---------------------------------------------------------------------------
# 1. Record a quiz attempt
# ---------------------------------------------------------------------------

class TestRecordQuizAttempt:
    def test_inserts_row_and_returns_it(self):
        client, builder = _mock_client()
        expected_row = {
            "id": "abc-123",
            "tenant_id": "t1",
            "user_id": "u1",
            "score_raw": 8,
            "score_pct": 80.0,
            "total_questions": 10,
        }
        builder.execute.return_value = _make_response([expected_row])

        service = AnalyticsService(client)
        attempt = QuizAttemptCreate(
            tenant_id="t1",
            user_id="u1",
            score_raw=8,
            score_pct=80.0,
            total_questions=10,
            topic_id="photosynthesis",
        )
        result = service.record_quiz_attempt(attempt)

        assert result == expected_row
        # Verify the correct table was targeted
        client.table.assert_called_with("quiz_attempts")
        builder.insert.assert_called_once()

    def test_payload_excludes_none_fields(self):
        client, builder = _mock_client()
        builder.execute.return_value = _make_response([{"id": "x"}])

        service = AnalyticsService(client)
        attempt = QuizAttemptCreate(
            tenant_id="t1",
            user_id="u1",
            score_raw=5,
            score_pct=50.0,
            total_questions=10,
            # course_id, lesson_id, topic_id intentionally omitted
        )
        service.record_quiz_attempt(attempt)

        inserted_data = builder.insert.call_args[0][0]
        assert "course_id" not in inserted_data
        assert "lesson_id" not in inserted_data


# ---------------------------------------------------------------------------
# 2. Record quiz answers
# ---------------------------------------------------------------------------

class TestRecordQuizAnswers:
    def test_inserts_all_answers_with_attempt_id(self):
        client, builder = _mock_client()
        returned_rows = [
            {"id": "r1", "question_id": "q1", "is_correct": True},
            {"id": "r2", "question_id": "q2", "is_correct": False},
        ]
        builder.execute.return_value = _make_response(returned_rows)

        service = AnalyticsService(client)
        answers = [
            QuizAnswerCreate(
                tenant_id="t1", user_id="u1",
                question_id="q1", is_correct=True,
            ),
            QuizAnswerCreate(
                tenant_id="t1", user_id="u1",
                question_id="q2", is_correct=False, error_type="concept",
            ),
        ]
        result = service.record_quiz_answers("attempt-001", answers)

        assert len(result) == 2
        client.table.assert_called_with("quiz_answers")
        inserted_rows = builder.insert.call_args[0][0]
        assert inserted_rows[0]["attempt_id"] == "attempt-001"
        assert inserted_rows[1]["attempt_id"] == "attempt-001"

    def test_empty_answers_returns_empty_list(self):
        client, builder = _mock_client()
        service = AnalyticsService(client)
        result = service.record_quiz_answers("attempt-001", [])
        assert result == []
        builder.insert.assert_not_called()


# ---------------------------------------------------------------------------
# 3. Create a new learner_topic_state (first attempt)
# ---------------------------------------------------------------------------

class TestUpsertTopicStateCreate:
    def test_creates_row_when_none_exists(self):
        client, builder = _mock_client()

        # get_topic_state returns None (no existing row)
        # first .execute() is for the SELECT in get_topic_state
        # second .execute() is for the INSERT in upsert_topic_state
        new_row = {
            "id": "new-id",
            "tenant_id": "t1",
            "user_id": "u1",
            "topic_id": "photosynthesis",
            "attempt_count": 1,
            "avg_score_pct": 60.0,
            "last_score_pct": 60.0,
            "mastery_score": 0.6,
            "weakness_level": "medium",
            "risk_level": "medium",
        }
        builder.execute.side_effect = [
            _make_response([]),       # SELECT → not found
            _make_response([new_row]),  # INSERT → new row
        ]

        service = AnalyticsService(client)
        result = service.upsert_topic_state(
            tenant_id="t1",
            user_id="u1",
            course_id=None,
            topic_id="photosynthesis",
            latest_score_pct=60.0,
        )

        assert result["attempt_count"] == 1
        assert result["avg_score_pct"] == 60.0
        assert result["weakness_level"] == "medium"
        assert result["risk_level"] == "medium"

    def test_initial_row_weakness_high_below_40(self):
        client, builder = _mock_client()
        row = {"id": "x", "attempt_count": 1, "avg_score_pct": 30.0,
               "last_score_pct": 30.0, "mastery_score": 0.3,
               "weakness_level": "high", "risk_level": "high"}
        builder.execute.side_effect = [
            _make_response([]),
            _make_response([row]),
        ]
        service = AnalyticsService(client)
        result = service.upsert_topic_state("t1", "u1", None, "algebra", 30.0)
        assert result["weakness_level"] == "high"
        assert result["risk_level"] == "high"


# ---------------------------------------------------------------------------
# 4. Update an existing learner_topic_state
# ---------------------------------------------------------------------------

class TestUpsertTopicStateUpdate:
    def test_rolling_average_is_correct(self):
        """
        Existing row: count=2, avg=50.0
        New score: 80.0
        Expected new avg: (50 * 2 + 80) / 3 = 60.0
        """
        client, builder = _mock_client()

        existing_row = {
            "id": "existing-id",
            "tenant_id": "t1",
            "user_id": "u1",
            "topic_id": "algebra",
            "attempt_count": 2,
            "avg_score_pct": 50.0,
            "last_score_pct": 50.0,
            "mastery_score": 0.5,
            "weakness_level": "medium",
            "risk_level": "medium",
        }
        updated_row = {
            **existing_row,
            "attempt_count": 3,
            "last_score_pct": 80.0,
            "avg_score_pct": 60.0,
            "mastery_score": 0.6,
            "weakness_level": "medium",
            "risk_level": "medium",
        }
        builder.execute.side_effect = [
            _make_response([existing_row]),   # SELECT
            _make_response([updated_row]),    # UPDATE
        ]

        service = AnalyticsService(client)
        result = service.upsert_topic_state("t1", "u1", None, "algebra", 80.0)

        assert result["attempt_count"] == 3
        assert result["avg_score_pct"] == 60.0
        assert result["mastery_score"] == 0.6

    def test_update_uses_existing_id(self):
        """Ensure the UPDATE targets the correct row by id."""
        client, builder = _mock_client()

        existing = {"id": "row-99", "attempt_count": 1, "avg_score_pct": 70.0,
                    "last_score_pct": 70.0}
        updated = {**existing, "attempt_count": 2, "avg_score_pct": 75.0,
                   "last_score_pct": 80.0, "mastery_score": 0.75,
                   "weakness_level": "low", "risk_level": "low"}
        builder.execute.side_effect = [
            _make_response([existing]),
            _make_response([updated]),
        ]

        service = AnalyticsService(client)
        service.upsert_topic_state("t1", "u1", None, "topic-x", 80.0)

        # Confirm .eq("id", "row-99") was called during the update
        eq_calls = [str(c) for c in builder.eq.call_args_list]
        assert any("row-99" in c for c in eq_calls)


# ---------------------------------------------------------------------------
# 5. Deriving weak_topics and at_risk_topics
# ---------------------------------------------------------------------------

class TestLearnerDashboard:
    def _make_state_row(self, topic_id, weakness, risk):
        return {
            "id": f"id-{topic_id}",
            "tenant_id": "t1", "user_id": "u1",
            "course_id": None, "topic_id": topic_id,
            "mastery_score": 0.5,
            "attempt_count": 2,
            "avg_score_pct": 55.0,
            "last_score_pct": 55.0,
            "weakness_level": weakness,
            "risk_level": risk,
            "last_seen_at": None,
            "updated_at": None,
        }

    def test_weak_and_at_risk_derivation(self):
        client, builder = _mock_client()

        states = [
            self._make_state_row("algebra", "high", "high"),   # weak + at risk
            self._make_state_row("biology", "medium", "low"),  # weak only
            self._make_state_row("history", "low", "medium"),  # at risk only
            self._make_state_row("physics", "low", "low"),     # neither
        ]
        builder.execute.side_effect = [
            _make_response(states),   # SELECT from learner_topic_state
            _make_response([{"score_pct": 60}, {"score_pct": 70}]),  # recent attempts
        ]

        service = AnalyticsService(client)
        dashboard = service.get_learner_dashboard("t1", "u1")

        assert set(dashboard.weak_topics) == {"algebra", "biology"}
        assert set(dashboard.at_risk_topics) == {"algebra", "history"}
        assert "physics" not in dashboard.weak_topics
        assert "physics" not in dashboard.at_risk_topics

    def test_recent_average_score_computed_correctly(self):
        client, builder = _mock_client()

        builder.execute.side_effect = [
            _make_response([]),   # no topic states
            _make_response([
                {"score_pct": 80},
                {"score_pct": 60},
                {"score_pct": 70},
            ]),
        ]

        service = AnalyticsService(client)
        dashboard = service.get_learner_dashboard("t1", "u1")

        assert dashboard.recent_average_score == pytest.approx(70.0)

    def test_no_attempts_gives_none_average(self):
        client, builder = _mock_client()
        builder.execute.side_effect = [
            _make_response([]),
            _make_response([]),
        ]
        service = AnalyticsService(client)
        dashboard = service.get_learner_dashboard("t1", "u1")
        assert dashboard.recent_average_score is None


# ---------------------------------------------------------------------------
# 6. Recommendations
# ---------------------------------------------------------------------------

class TestRecommendations:
    def test_add_recommendation_inserts_and_returns_row(self):
        client, builder = _mock_client()
        rec_row = {
            "id": "rec-1",
            "tenant_id": "t1",
            "user_id": "u1",
            "recommendation_type": "remediation",
            "topic_id": "algebra",
            "recommended_mode": "visual",
            "reason": "Below mastery threshold",
        }
        builder.execute.return_value = _make_response([rec_row])

        service = AnalyticsService(client)
        rec = RecommendationCreate(
            tenant_id="t1",
            user_id="u1",
            topic_id="algebra",
            recommendation_type="remediation",
            recommended_mode="visual",
            reason="Below mastery threshold",
        )
        result = service.add_recommendation(rec)

        assert result["recommendation_type"] == "remediation"
        client.table.assert_called_with("recommendation_history")

    def test_get_recent_recommendations_returns_list(self):
        client, builder = _mock_client()
        rows = [
            {"id": "r1", "recommendation_type": "remediation"},
            {"id": "r2", "recommendation_type": "advancement"},
        ]
        builder.execute.return_value = _make_response(rows)

        service = AnalyticsService(client)
        result = service.get_recent_recommendations("t1", "u1", limit=5)

        assert len(result) == 2
        assert result[0]["id"] == "r1"
        builder.limit.assert_called_with(5)

    def test_get_recent_recommendations_empty(self):
        client, builder = _mock_client()
        builder.execute.return_value = _make_response([])
        service = AnalyticsService(client)
        result = service.get_recent_recommendations("t1", "u1")
        assert result == []


# ---------------------------------------------------------------------------
# Helper function unit tests
# ---------------------------------------------------------------------------

class TestLevelHelpers:
    @pytest.mark.parametrize("score,expected", [
        (0,   "high"),
        (39,  "high"),
        (40,  "medium"),
        (69,  "medium"),
        (70,  "low"),
        (100, "low"),
    ])
    def test_weakness_level(self, score, expected):
        assert _weakness_level(score) == expected

    @pytest.mark.parametrize("score,expected", [
        (0,   "high"),
        (49,  "high"),
        (50,  "medium"),
        (74,  "medium"),
        (75,  "low"),
        (100, "low"),
    ])
    def test_risk_level(self, score, expected):
        assert _risk_level(score) == expected
