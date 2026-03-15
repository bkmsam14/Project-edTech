"""Recommendation handler - RECOMMEND workflow step"""
import logging
from database import SessionLocal
from models.lesson_model import Lesson
from utils.recommendation import generate_recommendations

logger = logging.getLogger(__name__)


async def recommendation_handler(context):
    """
    Generate personalized learning recommendations.

    Thin orchestrator wrapper: pulls data from context/DB,
    delegates to the recommendation agent in utils, returns results.

    Input (from context):
        - context.user_profile: User profile with mastery_levels
        - context.intermediate_results["retrieve_history"]: Past activities
        - context.request.lesson_id: Current lesson (optional)
        - context.request.context.get("depth", 3): Recommendation depth

    Output:
        - recommendations list with reasoning, total count, summary
    """
    try:
        user_profile = context.user_profile or {}
        mastery_levels = user_profile.get("mastery_levels", {})

        # Get learning history from previous workflow step
        history_result = context.intermediate_results.get("retrieve_history", {})
        learning_history = history_result if isinstance(history_result, list) else history_result.get("history", [])

        # Get depth from request context
        request_context = getattr(context.request, "context", {}) or {}
        depth = request_context.get("depth", 3)

        # Get current lesson id
        current_lesson_id = context.request.lesson_id

        # Fetch available lessons from DB
        available_lessons = _fetch_available_lessons()

        # Delegate to recommendation agent (pure logic)
        result = generate_recommendations(
            available_lessons=available_lessons,
            mastery_levels=mastery_levels,
            learning_history=learning_history,
            current_lesson_id=current_lesson_id,
            depth=depth
        )

        logger.info(
            f"Generated {result['total_recommendations']} recommendations "
            f"for user {user_profile.get('user_id')}"
        )

        return result

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise


def _fetch_available_lessons() -> list:
    """Fetch all lessons from DB and convert to dicts."""
    try:
        db = SessionLocal()
        try:
            lessons = db.query(Lesson).all()
            return [lesson.to_dict() for lesson in lessons]
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not fetch lessons from DB: {e}")
        return []
