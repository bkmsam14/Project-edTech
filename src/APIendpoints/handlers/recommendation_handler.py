"""Recommendation handler - RECOMMEND workflow step"""
import logging
from database import SessionLocal
from models.lesson_model import Lesson

logger = logging.getLogger(__name__)


async def recommendation_handler(context):
    """
    Generate personalized learning recommendations.

    Uses user's mastery levels and learning history to recommend next topics.

    Input (from context):
        - context.user_profile: User profile with mastery_levels
        - context.intermediate_results["learning_history"]: Past activities
        - context.request.lesson_id: Current lesson (optional)

    Output:
        - recommendations: List of recommended lessons
        - reasoning: Why these were recommended
        - stores in context.intermediate_results["recommendations"]
    """
    try:
        user_profile = context.user_profile or {}
        mastery_levels = user_profile.get("mastery_levels", {})
        learning_history = context.intermediate_results.get("learning_history", [])

        db = SessionLocal()
        try:
            # Get all lessons
            all_lessons = db.query(Lesson).all()

            # Score each lesson for recommendation
            scored_lessons = []

            for lesson in all_lessons:
                score = _calculate_recommendation_score(
                    lesson,
                    mastery_levels,
                    learning_history,
                    context.request.lesson_id
                )

                if score > 0:
                    scored_lessons.append((lesson, score))

            # Sort by score and get top recommendations
            sorted_lessons = sorted(scored_lessons, key=lambda x: x[1], reverse=True)
            top_recommendations = sorted_lessons[:5]

            recommendations = []
            reasoning = []

            for lesson, score in top_recommendations:
                recommendations.append({
                    "lesson_id": lesson.lesson_id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "subject": lesson.subject,
                    "difficulty": lesson.difficulty,
                    "estimated_time_minutes": lesson.estimated_time_minutes,
                    "confidence_score": round(score, 2)
                })

                # Add reasoning
                reasoning.append(_generate_reasoning(lesson, mastery_levels, score))

            logger.info(f"Generated {len(recommendations)} recommendations for user {user_profile.get('user_id')}")

            return {
                "recommendations": recommendations,
                "reasoning": reasoning,
                "total_recommendations": len(recommendations)
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise


def _calculate_recommendation_score(lesson: 'Lesson', mastery_levels: dict,
                                   learning_history: list, current_lesson_id: str) -> float:
    """
    Calculate recommendation score for a lesson.

    Factors:
    - Prerequisites completed (high factor)
    - Difficulty progression (medium factor)
    - Not already completed (filter)
    - Subject interest (low factor)
    """
    if lesson.lesson_id == current_lesson_id:
        return 0.0  # Don't recommend current lesson

    # Check if already completed
    completed_lessons = set(h.get("lesson_id") for h in learning_history)
    if lesson.lesson_id in completed_lessons:
        return 0.0

    score = 0.5  # Base score

    # Check prerequisites
    if lesson.prerequisites:
        prerequisites_met = all(
            prereq in completed_lessons or prereq in mastery_levels
            for prereq in lesson.prerequisites
        )
        if prerequisites_met:
            score += 0.3  # Strong positive if prerequisites are met
        else:
            return 0.0  # Can't recommend without prerequisites

    # Difficulty progression: recommend next level up
    current_difficulty_score = _difficulty_to_score(lesson.difficulty)
    avg_completed_difficulty = _get_avg_completed_difficulty(learning_history)

    if current_difficulty_score == avg_completed_difficulty + 1:
        score += 0.2  # Good progression step
    elif current_difficulty_score > avg_completed_difficulty + 1:
        score -= 0.1  # Too hard

    return max(0.0, score)


def _difficulty_to_score(difficulty: str) -> float:
    """Convert difficulty level to numeric score"""
    difficulty_map = {
        "beginner": 1.0,
        "intermediate": 2.0,
        "advanced": 3.0
    }
    return difficulty_map.get(difficulty, 2.0)


def _get_avg_completed_difficulty(learning_history: list) -> float:
    """Get average difficulty of completed lessons"""
    completed = [h for h in learning_history if h.get("completion_status") == "completed"]
    if not completed:
        return 0.5  # Start with beginner

    # In a real system, would look up lesson difficulty, but we'll estimate from score
    avg_score = sum(h.get("score", 0) for h in completed) / len(completed) if completed else 0.5

    if avg_score < 0.4:
        return 1.0  # Beginner
    elif avg_score < 0.7:
        return 1.5  # Beginner-Intermediate
    else:
        return 2.0  # Intermediate+


def _generate_reasoning(lesson: 'Lesson', mastery_levels: dict, score: float) -> str:
    """Generate human-readable reasoning for recommendation"""
    if score > 0.8:
        return f"Strong match: '{lesson.title}' builds on your current knowledge"
    elif score > 0.6:
        return f"Recommended: '{lesson.title}' is the next step in your learning path"
    else:
        return f"Suggested: '{lesson.title}' aligns with your learning goals"
