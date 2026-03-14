"""Retrieval handler - RETRIEVE_LESSON and RETRIEVE_HISTORY workflow steps"""
import logging
from database import SessionLocal
from models.lesson_model import Lesson
from models.history_model import LearningHistory

logger = logging.getLogger(__name__)


async def retrieve_lesson_handler(context):
    """
    Retrieve lesson content from database.

    Input (from context):
        - context.request.lesson_id: Lesson identifier

    Output:
        - lesson_content: Lesson details and metadata
        - retrieved_chunks: Content chunks for RAG
        - stores in context.lesson_content and context.retrieved_chunks
    """
    try:
        lesson_id = context.request.lesson_id
        if not lesson_id:
            logger.warning("No lesson_id provided")
            return {"error": "lesson_id required"}

        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()

            if not lesson:
                logger.warning(f"Lesson {lesson_id} not found")
                return {"error": f"Lesson {lesson_id} not found"}

            # Get chunks for RAG
            lesson.generate_chunks()
            chunks = lesson.get_chunks()

            lesson_content = {
                "lesson_id": lesson.lesson_id,
                "title": lesson.title,
                "description": lesson.description,
                "subject": lesson.subject,
                "content": lesson.content,
                "difficulty": lesson.difficulty,
                "estimated_time_minutes": lesson.estimated_time_minutes,
                "tags": lesson.tags,
                "prerequisites": lesson.prerequisites
            }

            logger.info(f"Retrieved lesson {lesson_id} with {len(chunks)} chunks")

            # Return both lesson content and chunks
            return {
                "lesson_content": lesson_content,
                "retrieved_chunks": chunks
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error retrieving lesson: {e}")
        raise


async def retrieve_history_handler(context):
    """
    Retrieve user's learning history from database.

    Input (from context):
        - context.user_profile: User data with user_id

    Output:
        - learning_history: List of past learning activities
        - stores in context.intermediate_results["learning_history"]
    """
    try:
        user_id = context.user_profile.get("user_id") if context.user_profile else None
        if not user_id:
            logger.warning("No user_id in context")
            return {"history": []}

        db = SessionLocal()
        try:
            # Get user's learning history
            history_records = db.query(LearningHistory)\
                .filter(LearningHistory.user_id == user_id)\
                .order_by(LearningHistory.created_at.desc())\
                .all()

            history = [record.to_dict() for record in history_records]

            logger.info(f"Retrieved {len(history)} history records for user {user_id}")
            return {"history": history}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise
