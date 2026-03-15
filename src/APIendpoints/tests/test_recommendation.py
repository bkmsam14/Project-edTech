"""
Unit tests for the Recommendation Agent

Tests generate_recommendations() with mock lesson and history data.
"""

import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.recommendation import generate_recommendations


# ============================================================================
# MOCK DATA
# ============================================================================

MOCK_LESSONS = [
    {
        "lesson_id": "lesson_001", "title": "Intro to Biology",
        "description": "Basic biology concepts", "subject": "Biology",
        "difficulty": "beginner", "estimated_time_minutes": 30,
        "prerequisites": [], "tags": ["biology", "intro"]
    },
    {
        "lesson_id": "lesson_002", "title": "Cell Structure",
        "description": "Understanding cells and organelles", "subject": "Biology",
        "difficulty": "intermediate", "estimated_time_minutes": 45,
        "prerequisites": ["lesson_001"], "tags": ["biology", "cells"]
    },
    {
        "lesson_id": "lesson_003", "title": "Intro to Math",
        "description": "Basic arithmetic and algebra", "subject": "Math",
        "difficulty": "beginner", "estimated_time_minutes": 25,
        "prerequisites": [], "tags": ["math", "intro"]
    },
    {
        "lesson_id": "lesson_004", "title": "Advanced Genetics",
        "description": "DNA and heredity", "subject": "Biology",
        "difficulty": "advanced", "estimated_time_minutes": 60,
        "prerequisites": ["lesson_001", "lesson_002"], "tags": ["biology", "genetics"]
    },
    {
        "lesson_id": "lesson_005", "title": "Algebra II",
        "description": "Advanced algebra concepts", "subject": "Math",
        "difficulty": "intermediate", "estimated_time_minutes": 40,
        "prerequisites": ["lesson_003"], "tags": ["math", "algebra"]
    },
]

HISTORY_WITH_COMPLETIONS = [
    {"lesson_id": "lesson_001", "score": 0.85, "completion_status": "completed", "activity_type": "quiz_attempt"},
    {"lesson_id": "lesson_003", "score": 0.70, "completion_status": "completed", "activity_type": "quiz_attempt"},
]

EMPTY_HISTORY = []


# ============================================================================
# TESTS
# ============================================================================

def test_fresh_user():
    """Fresh user with no history should get beginner lessons."""
    result = generate_recommendations(
        available_lessons=MOCK_LESSONS,
        mastery_levels={},
        learning_history=EMPTY_HISTORY,
        depth=3
    )

    assert result["total_recommendations"] > 0, "Should return at least one recommendation"
    assert result["depth_requested"] == 3
    assert "recommendations" in result
    assert "summary" in result

    # Should not recommend lessons with unmet prerequisites
    rec_ids = [r["lesson_id"] for r in result["recommendations"]]
    assert "lesson_004" not in rec_ids, "Advanced Genetics requires prereqs that are not met"

    print(f"  ✓ Fresh user: {result['total_recommendations']} recommendations")


def test_user_with_history():
    """User with completed lessons should get appropriate next steps."""
    result = generate_recommendations(
        available_lessons=MOCK_LESSONS,
        mastery_levels={"Biology": 0.85, "Math": 0.70},
        learning_history=HISTORY_WITH_COMPLETIONS,
        depth=3
    )

    rec_ids = [r["lesson_id"] for r in result["recommendations"]]

    # lesson_001 and lesson_003 are completed, should not appear
    assert "lesson_001" not in rec_ids, "Completed lesson should not be recommended"
    assert "lesson_003" not in rec_ids, "Completed lesson should not be recommended"

    # lesson_002 (Cell Structure) should be recommended — prereq lesson_001 is completed
    assert "lesson_002" in rec_ids, "Cell Structure should be recommended (prereq met)"

    print(f"  ✓ User with history: recommended {rec_ids}")


def test_depth_parameter():
    """Depth parameter should limit number of recommendations."""
    result_1 = generate_recommendations(
        available_lessons=MOCK_LESSONS,
        mastery_levels={},
        learning_history=EMPTY_HISTORY,
        depth=1
    )

    result_5 = generate_recommendations(
        available_lessons=MOCK_LESSONS,
        mastery_levels={},
        learning_history=EMPTY_HISTORY,
        depth=5
    )

    assert result_1["total_recommendations"] <= 1, "Depth=1 should return at most 1"
    assert result_1["depth_requested"] == 1
    assert result_5["depth_requested"] == 5

    print(f"  ✓ Depth=1: {result_1['total_recommendations']}, Depth=5: {result_5['total_recommendations']}")


def test_current_lesson_excluded():
    """Current lesson should be excluded from recommendations."""
    result = generate_recommendations(
        available_lessons=MOCK_LESSONS,
        mastery_levels={},
        learning_history=EMPTY_HISTORY,
        current_lesson_id="lesson_001",
        depth=5
    )

    rec_ids = [r["lesson_id"] for r in result["recommendations"]]
    assert "lesson_001" not in rec_ids, "Current lesson should be excluded"

    print(f"  ✓ Current lesson excluded: {rec_ids}")


def test_empty_lessons():
    """Empty lessons list should return empty recommendations gracefully."""
    result = generate_recommendations(
        available_lessons=[],
        mastery_levels={},
        learning_history=EMPTY_HISTORY,
        depth=3
    )

    assert result["total_recommendations"] == 0
    assert result["recommendations"] == []
    assert "summary" in result

    print(f"  ✓ Empty lessons: graceful empty result")


def test_recommendation_has_reasoning():
    """Each recommendation should include a reasoning string."""
    result = generate_recommendations(
        available_lessons=MOCK_LESSONS,
        mastery_levels={},
        learning_history=EMPTY_HISTORY,
        depth=3
    )

    for rec in result["recommendations"]:
        assert "reasoning" in rec, f"Recommendation {rec['lesson_id']} missing reasoning"
        assert len(rec["reasoning"]) > 0, f"Reasoning for {rec['lesson_id']} is empty"
        assert "confidence_score" in rec, f"Recommendation {rec['lesson_id']} missing confidence_score"

    print(f"  ✓ All recommendations have reasoning and confidence scores")


def test_subject_gap_bonus():
    """Lessons in weak subjects should score higher."""
    # User is weak in Math (0.3) but strong in Biology (0.9)
    result = generate_recommendations(
        available_lessons=MOCK_LESSONS,
        mastery_levels={"Biology": 0.9, "Math": 0.3},
        learning_history=EMPTY_HISTORY,
        depth=5
    )

    # Find Math and Biology recommendations and compare scores
    math_recs = [r for r in result["recommendations"] if r["subject"] == "Math"]
    bio_recs = [r for r in result["recommendations"] if r["subject"] == "Biology"]

    if math_recs and bio_recs:
        # At same difficulty level (beginner), Math should score higher due to gap bonus
        math_beginner = [r for r in math_recs if r["difficulty"] == "beginner"]
        bio_beginner = [r for r in bio_recs if r["difficulty"] == "beginner"]

        if math_beginner and bio_beginner:
            assert math_beginner[0]["confidence_score"] >= bio_beginner[0]["confidence_score"], \
                "Math (weak subject) should score >= Biology (strong subject) at same difficulty"

    print(f"  ✓ Subject gap bonus working")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    print("\n🧪 Running Recommendation Agent Tests\n")

    test_fresh_user()
    test_user_with_history()
    test_depth_parameter()
    test_current_lesson_excluded()
    test_empty_lessons()
    test_recommendation_has_reasoning()
    test_subject_gap_bonus()

    print("\n✅ All recommendation tests passed!\n")
