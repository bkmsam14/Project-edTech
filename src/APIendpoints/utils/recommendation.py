"""Recommendation agent - personalized learning path recommendations

Handles:
- Lesson scoring and ranking
- Difficulty progression analysis
- AI-powered reasoning generation (with heuristic fallback)
- Depth-aware recommendation filtering
"""
import logging
from typing import Dict, List, Any, Optional

from config import RECOMMENDATION_DEPTH_LIMIT

logger = logging.getLogger(__name__)


# ============================================================
# PUBLIC ENTRY POINT
# ============================================================

def generate_recommendations(
    available_lessons: List[Dict[str, Any]],
    mastery_levels: Dict[str, float],
    learning_history: List[Dict[str, Any]],
    current_lesson_id: Optional[str] = None,
    depth: int = 3
) -> Dict[str, Any]:
    """
    Generate personalized learning recommendations.

    Args:
        available_lessons: List of lesson dicts (from Lesson.to_dict())
        mastery_levels: Dict mapping subject/topic -> mastery score (0.0-1.0)
        learning_history: List of history dicts (from LearningHistory.to_dict())
        current_lesson_id: ID of the lesson the user is currently on (to exclude)
        depth: Number of recommendations to return

    Returns:
        Dict with recommendations, reasoning, summary, and metadata
    """
    try:
        if not available_lessons:
            logger.warning("No lessons available for recommendations")
            return _create_empty_recommendations(depth)

        # Clamp depth
        depth = max(1, min(depth, RECOMMENDATION_DEPTH_LIMIT))

        # Step 1: Build set of completed lesson IDs
        completed_lesson_ids = _get_completed_lesson_ids(learning_history)

        # Step 2: Score each lesson
        scored_lessons = []
        for lesson in available_lessons:
            score = _calculate_recommendation_score(
                lesson, mastery_levels, completed_lesson_ids,
                learning_history, current_lesson_id
            )
            if score > 0:
                scored_lessons.append((lesson, score))

        if not scored_lessons:
            logger.info("No qualifying lessons for recommendations")
            return _create_empty_recommendations(depth)

        # Step 3: Sort by score descending, take top `depth`
        scored_lessons.sort(key=lambda x: x[1], reverse=True)
        top_lessons = scored_lessons[:depth]

        # Step 4: Build recommendation entries with reasoning
        recommendations = []
        strategy_used = "heuristic"

        for lesson, score in top_lessons:
            reasoning, strategy = _generate_reasoning(
                lesson, mastery_levels, score, learning_history
            )
            if strategy == "ai":
                strategy_used = "ai"

            recommendations.append({
                "lesson_id": lesson.get("lesson_id"),
                "title": lesson.get("title"),
                "description": lesson.get("description"),
                "subject": lesson.get("subject"),
                "difficulty": lesson.get("difficulty"),
                "estimated_time_minutes": lesson.get("estimated_time_minutes", 30),
                "confidence_score": round(score, 2),
                "reasoning": reasoning
            })

        # Step 5: Generate summary
        summary = _generate_summary(recommendations, depth)

        result = {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "depth_requested": depth,
            "strategy_used": strategy_used,
            "summary": summary
        }

        logger.info(
            f"Generated {len(recommendations)} recommendations "
            f"(depth={depth}, strategy={strategy_used})"
        )

        return result

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise


# ============================================================
# PRIVATE HELPERS
# ============================================================

def _get_completed_lesson_ids(learning_history: List[Dict[str, Any]]) -> set:
    """Extract set of completed lesson IDs from learning history."""
    return {
        h.get("lesson_id")
        for h in learning_history
        if h.get("completion_status") == "completed" or h.get("lesson_id")
    }


def _calculate_recommendation_score(
    lesson: Dict[str, Any],
    mastery_levels: Dict[str, float],
    completed_lesson_ids: set,
    learning_history: List[Dict[str, Any]],
    current_lesson_id: Optional[str]
) -> float:
    """
    Score a lesson for recommendation (0.0 = skip, higher = better).

    Factors:
    - Base score: 0.5
    - Prerequisites met: +0.3 (unmet: return 0.0)
    - Difficulty progression: +0.2 (next level), -0.1 (too hard)
    - Subject mastery gap: +0.15 (user is weak in this subject)
    """
    lesson_id = lesson.get("lesson_id")

    # Filter: skip current lesson
    if lesson_id == current_lesson_id:
        return 0.0

    # Filter: skip completed lessons
    if lesson_id in completed_lesson_ids:
        return 0.0

    score = 0.5  # Base score

    # Prerequisites check
    prerequisites = lesson.get("prerequisites") or []
    if prerequisites:
        prerequisites_met = all(
            prereq in completed_lesson_ids or prereq in mastery_levels
            for prereq in prerequisites
        )
        if prerequisites_met:
            score += 0.3
        else:
            return 0.0  # Can't recommend without prerequisites

    # Difficulty progression
    lesson_difficulty = _difficulty_to_score(lesson.get("difficulty", "intermediate"))
    avg_completed = _get_avg_completed_difficulty(learning_history)

    if lesson_difficulty == avg_completed + 1:
        score += 0.2  # Good next step
    elif lesson_difficulty > avg_completed + 1:
        score -= 0.1  # Too hard

    # Subject mastery gap bonus
    score += _calculate_subject_gap_bonus(lesson, mastery_levels)

    return max(0.0, score)


def _difficulty_to_score(difficulty: str) -> float:
    """Convert difficulty string to numeric score."""
    difficulty_map = {
        "beginner": 1.0,
        "intermediate": 2.0,
        "advanced": 3.0
    }
    return difficulty_map.get(difficulty, 2.0)


def _get_avg_completed_difficulty(learning_history: List[Dict[str, Any]]) -> float:
    """Compute average difficulty from completed history entries."""
    completed = [h for h in learning_history if h.get("completion_status") == "completed"]
    if not completed:
        return 0.5  # Start with beginner

    avg_score = sum(h.get("score", 0) for h in completed) / len(completed)

    # Normalize if scores are integers > 1 (from assessment handler)
    if avg_score > 1.0:
        avg_score = avg_score / 100.0

    if avg_score < 0.4:
        return 1.0  # Beginner
    elif avg_score < 0.7:
        return 1.5  # Beginner-Intermediate
    else:
        return 2.0  # Intermediate+


def _calculate_subject_gap_bonus(
    lesson: Dict[str, Any],
    mastery_levels: Dict[str, float]
) -> float:
    """
    Give a bonus if the user's mastery in this lesson's subject is low.
    Surfaces subjects the learner needs work on.
    """
    subject = lesson.get("subject", "")
    if not subject or not mastery_levels:
        return 0.0

    subject_mastery = mastery_levels.get(subject, 0.0)
    if subject_mastery < 0.5:
        return 0.15  # Bonus for weak subject
    return 0.0


def _generate_reasoning(
    lesson: Dict[str, Any],
    mastery_levels: Dict[str, float],
    score: float,
    learning_history: List[Dict[str, Any]]
) -> tuple:
    """
    Generate reasoning for why a lesson is recommended.
    Tries AI first, falls back to heuristic.

    Returns:
        Tuple of (reasoning_string, strategy_used)
    """
    # Try AI-powered reasoning
    ai_result = _generate_ai_reasoning(lesson, mastery_levels, score, learning_history)
    if ai_result:
        return ai_result, "ai"

    # Fallback to heuristic
    return _generate_heuristic_reasoning(lesson, mastery_levels, score), "heuristic"


def _generate_ai_reasoning(
    lesson: Dict[str, Any],
    mastery_levels: Dict[str, float],
    score: float,
    learning_history: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Call Ollama to produce a 1-2 sentence personalized reasoning.
    Returns None if unavailable or response invalid.
    """
    try:
        from utils.ai_utils import is_ollama_available, call_local_model

        if not is_ollama_available():
            return None

        prompt = _build_recommendation_prompt(
            lesson, mastery_levels, score, len(learning_history)
        )

        result = call_local_model(prompt, temperature=0.5)

        if result and len(result.strip()) > 10 and len(result.strip()) < 500:
            return result.strip()

        return None

    except Exception as e:
        logger.debug(f"AI reasoning failed, using heuristic: {e}")
        return None


def _build_recommendation_prompt(
    lesson: Dict[str, Any],
    mastery_levels: Dict[str, float],
    score: float,
    completed_count: int
) -> str:
    """Build structured prompt for 1-2 sentence recommendation reasoning."""
    subject = lesson.get("subject", "this subject")
    subject_mastery = mastery_levels.get(subject, 0.0)

    if subject_mastery < 0.4:
        level = "beginner"
    elif subject_mastery < 0.7:
        level = "intermediate"
    else:
        level = "advanced"

    return (
        f"You are an educational advisor. In 1-2 SHORT sentences, explain why "
        f"this lesson is a good next step for the student.\n\n"
        f"STUDENT CONTEXT:\n"
        f"- Completed {completed_count} lessons so far\n"
        f"- Mastery in {subject}: {subject_mastery:.0%}\n"
        f"- Current level: {level}\n\n"
        f"RECOMMENDED LESSON:\n"
        f"- Title: {lesson.get('title', 'Unknown')}\n"
        f"- Subject: {subject}\n"
        f"- Difficulty: {lesson.get('difficulty', 'Unknown')}\n"
        f"- Description: {(lesson.get('description', '') or '')[:200]}\n\n"
        f"IMPORTANT: Keep it simple, encouraging, and under 2 sentences. "
        f"Use plain language.\n\nREASONING:"
    )


def _generate_heuristic_reasoning(
    lesson: Dict[str, Any],
    mastery_levels: Dict[str, float],
    score: float
) -> str:
    """Rule-based reasoning fallback."""
    title = lesson.get("title", "this lesson")

    if score > 0.8:
        return f"Strong match: '{title}' builds directly on your current knowledge and is the ideal next step."
    elif score > 0.6:
        return f"Recommended: '{title}' is the natural next step in your learning path."
    else:
        return f"Suggested: '{title}' aligns with your learning goals and will help fill knowledge gaps."


def _generate_summary(recommendations: List[Dict[str, Any]], depth: int) -> str:
    """Generate a human-readable summary of the recommendation set."""
    count = len(recommendations)
    if count == 0:
        return "No recommendations available at this time. You may have completed all available lessons."

    subjects = list({r.get("subject", "Unknown") for r in recommendations})
    subjects_str = ", ".join(subjects)

    if count == 1:
        return f"We found 1 recommended lesson for you in {subjects_str}."
    return f"We found {count} recommended lessons for you across {subjects_str}."


def _create_empty_recommendations(depth: int) -> Dict[str, Any]:
    """Return an empty-but-valid recommendations dict."""
    return {
        "recommendations": [],
        "total_recommendations": 0,
        "depth_requested": depth,
        "strategy_used": "heuristic",
        "summary": "No recommendations available. You may have completed all available lessons."
    }
