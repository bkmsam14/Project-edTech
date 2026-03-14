"""Assessment handler - ASSESS_QUIZ workflow step"""
import logging
import uuid
from database import SessionLocal
from models.history_model import LearningHistory
from utils.assessment import assess_quiz

logger = logging.getLogger(__name__)


async def assess_quiz_handler(context):
    """
    Grade quiz answers and provide comprehensive feedback using Assessment Agent.

    Input (from context):
        - context.intermediate_results["quiz"]: Quiz data with questions and correct answers
        - context.intermediate_results["answers"]: Submitted answers as dict {question_id: answer}
        - context.user_profile: User data
        - context.request.lesson_id: Lesson being assessed

    Output:
        - quiz_id: Reference to the quiz
        - score: Number of correct answers (int)
        - total: Total number of questions (int)
        - percentage: Score as percentage (float 0-100)
        - mastery_level: "high" | "medium" | "low"
        - weak_concepts: List of struggling concept tags
        - strong_concepts: List of mastered concept tags
        - feedback: Encouraging general feedback
        - detailed_feedback: Per-question feedback with explanations
        - summary: Human-readable assessment summary
        - recommendations: Personalized learning suggestions
        - passed: Whether user passed (>=80% for high mastery)

    Also stores result in learning_history database.
    """
    try:
        # Get quiz and answers
        quiz_data = context.intermediate_results.get("quiz", {})
        answers = context.intermediate_results.get("answers", {})

        if not quiz_data or not quiz_data.get("questions"):
            logger.warning("No quiz data for assessment")
            return {
                "score": 0,
                "total": 0,
                "percentage": 0.0,
                "mastery_level": "low",
                "weak_concepts": [],
                "strong_concepts": [],
                "feedback": "Unable to assess - missing quiz data",
                "detailed_feedback": [],
                "summary": "Assessment not completed",
                "recommendations": ["Please provide a valid quiz"],
                "passed": False,
                "message": "Unable to assess - missing quiz data"
            }

        if not answers:
            logger.warning("No answers provided for assessment")
            return {
                "score": 0,
                "total": len(quiz_data.get("questions", [])),
                "percentage": 0.0,
                "mastery_level": "low",
                "weak_concepts": [],
                "strong_concepts": [],
                "feedback": "No answers provided",
                "detailed_feedback": [],
                "summary": "Quiz not completed",
                "recommendations": ["Complete the quiz to receive feedback"],
                "passed": False,
                "message": "Unable to assess - no answers provided"
            }

        # Use the comprehensive assessment agent
        assessment_result = assess_quiz(quiz_data, answers)

        # Add pass/fail based on mastery level
        # High mastery (>=80%) = passed
        assessment_result["passed"] = assessment_result["mastery_level"] == "high"

        # Add difficulty and quiz_id for tracking
        assessment_result["difficulty"] = quiz_data.get("difficulty", "medium")

        # Save to learning history (if database enabled)
        if context.user_profile:
            _save_assessment_to_history(
                context.user_profile.get("user_id"),
                context.request.lesson_id,
                assessment_result["score"],
                assessment_result["total"],
                assessment_result["percentage"],
                assessment_result["mastery_level"],
                answers,
                assessment_result.get("detailed_feedback", [])
            )

        logger.info(
            f"Assessment complete: {assessment_result['percentage']:.1f}% "
            f"({assessment_result['score']}/{assessment_result['total']}), "
            f"Mastery: {assessment_result['mastery_level']}, "
            f"Weak concepts: {assessment_result['weak_concepts']}"
        )

        return assessment_result

    except Exception as e:
        logger.error(f"Error assessing quiz: {e}")
        raise


def _save_assessment_to_history(user_id: str, lesson_id: str, score: int, total: int,
                               percentage: float, mastery_level: str,
                               answers: dict, feedback_items: list) -> None:
    """Save assessment result to learning history database"""
    try:
        db = SessionLocal()
        try:
            history_record = LearningHistory(
                history_id=f"hist_{uuid.uuid4().hex[:12]}",
                user_id=user_id,
                lesson_id=lesson_id,
                activity_type="assessment",
                score=score,
                total=total,
                percentage=percentage,
                mastery_level=mastery_level,
                completion_status="completed",
                answers=answers,
                feedback=feedback_items
            )

            db.add(history_record)
            db.commit()

            logger.info(f"Saved assessment to history for user {user_id}: {mastery_level}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error saving assessment to history: {e}")
        # Don't raise - assessment was successful, just history save failed
