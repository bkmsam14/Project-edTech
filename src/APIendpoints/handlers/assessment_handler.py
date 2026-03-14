"""Assessment handler - ASSESS_QUIZ workflow step"""
import logging
import uuid
from database import SessionLocal
from models.history_model import LearningHistory
from utils.quiz_generator import calculate_quiz_score, generate_quiz_feedback

logger = logging.getLogger(__name__)


async def assess_quiz_handler(context):
    """
    Grade quiz answers and provide feedback.

    Input (from context):
        - context.request.message or context.intermediate_results: Submitted answers
        - context.intermediate_results["quiz"]: Quiz data with correct answers
        - context.user_profile: User data
        - context.request.lesson_id: Lesson being assessed

    Output:
        - score: Score as percentage (0-100)
        - feedback: Detailed feedback per question
        - passed: Whether user passed the quiz
        - stores in context.intermediate_results["assessment"]

    Also stores result in learning_history database.
    """
    try:
        # Get quiz and answers
        quiz_data = context.intermediate_results.get("quiz", {})
        questions = quiz_data.get("questions", [])

        # Get user's answers from context
        answers = context.intermediate_results.get("answers", {})

        if not answers or not questions:
            logger.warning("No answers or questions for assessment")
            return {
                "score": 0.0,
                "percentage": 0,
                "feedback": [],
                "passed": False,
                "message": "Unable to assess - missing answers or quiz"
            }

        # Calculate score
        score = calculate_quiz_score(answers, questions)
        percentage = round(score * 100, 1)

        # Generate detailed feedback
        feedback = generate_quiz_feedback(answers, questions)

        # Determine if passed (70% threshold)
        passed = percentage >= 70

        assessment_result = {
            "score": score,
            "percentage": percentage,
            "passed": passed,
            "num_correct": sum(1 for f in feedback if f["is_correct"]),
            "num_total": len(questions),
            "feedback": feedback,
            "quiz_id": quiz_data.get("quiz_id"),
            "difficulty": quiz_data.get("difficulty", "medium")
        }

        # Save to learning history
        if context.user_profile:
            _save_assessment_to_history(
                context.user_profile.get("user_id"),
                context.request.lesson_id,
                score,
                answers,
                feedback
            )

        logger.info(f"Assessment complete: {percentage}% ({sum(1 for f in feedback if f['is_correct'])}/{len(questions)})")

        return assessment_result

    except Exception as e:
        logger.error(f"Error assessing quiz: {e}")
        raise


def _save_assessment_to_history(user_id: str, lesson_id: str, score: float,
                               answers: dict, feedback: list) -> None:
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
                completion_status="completed",
                answers=answers,
                feedback=feedback
            )

            db.add(history_record)
            db.commit()

            logger.info(f"Saved assessment to history for user {user_id}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error saving assessment to history: {e}")
        # Don't raise - assessment was successful, just history save failed
