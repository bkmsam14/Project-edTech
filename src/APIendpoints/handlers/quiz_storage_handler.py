"""
Quiz storage handler - Saves quiz attempts and results to Supabase
"""

import logging
from datetime import datetime
from typing import Dict, List, Any
from database import get_supabase_admin

logger = logging.getLogger(__name__)


async def save_quiz_attempt(
    user_id: str,
    quiz_data: Dict[str, Any],
    answers: Dict[str, str],
    assessment_result: Dict[str, Any]
) -> bool:
    """
    Save quiz attempt and individual question results to Supabase

    Args:
        user_id: User ID
        quiz_data: Quiz metadata and questions
        answers: User's answers {question_id: answer}
        assessment_result: Assessment results from assessment_handler

    Returns:
        bool: True if saved successfully
    """
    try:
        supabase_admin = get_supabase_admin()

        # Calculate duration if timestamps available
        duration_seconds = None
        if quiz_data.get("started_at") and quiz_data.get("completed_at"):
            start = datetime.fromisoformat(quiz_data["started_at"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(quiz_data["completed_at"].replace("Z", "+00:00"))
            duration_seconds = int((end - start).total_seconds())

        # Prepare quiz attempt data
        attempt_data = {
            "user_id": user_id,
            "quiz_id": quiz_data.get("quiz_id", f"quiz_{datetime.utcnow().timestamp()}"),
            "lesson_id": quiz_data.get("lesson_id"),
            "subject": quiz_data.get("subject"),
            "topic": quiz_data.get("topic"),
            "quiz_type": quiz_data.get("quiz_type", "practice"),
            "difficulty": quiz_data.get("difficulty", "medium"),
            "total_questions": assessment_result.get("total", len(quiz_data.get("questions", []))),
            "correct_count": assessment_result.get("score", 0),
            "incorrect_count": assessment_result.get("total", 0) - assessment_result.get("score", 0),
            "skipped_count": 0,  # Can be enhanced later
            "score_pct": assessment_result.get("percentage", 0.0),
            "passed": assessment_result.get("passed", False),
            "started_at": quiz_data.get("started_at", datetime.utcnow().isoformat()),
            "completed_at": datetime.utcnow().isoformat(),
            "duration_seconds": duration_seconds,
            "weak_topics": assessment_result.get("weak_concepts", []),
            "strong_topics": assessment_result.get("strong_concepts", [])
        }

        # Insert quiz attempt
        attempt_response = supabase_admin.table("quiz_attempts").insert(attempt_data).execute()

        if not attempt_response.data:
            logger.error("Failed to insert quiz attempt")
            return False

        attempt_id = attempt_response.data[0]["id"]
        logger.info(f"Saved quiz attempt {attempt_id} for user {user_id}")

        # Insert individual question results
        questions = quiz_data.get("questions", [])
        question_data_list = []

        for idx, question in enumerate(questions):
            question_id = question.get("question_id", f"q_{idx}")
            user_answer = answers.get(question_id)
            correct_answer = question.get("correct_answer")

            question_data = {
                "attempt_id": attempt_id,
                "user_id": user_id,
                "question_id": question_id,
                "question_text": question.get("question_text", question.get("question", "")),
                "question_type": question.get("type", "multiple_choice"),
                "topic_tag": question.get("concept_tag", question.get("topic")),
                "correct_answer": correct_answer,
                "user_answer": user_answer,
                "is_correct": user_answer == correct_answer if user_answer else False,
                "time_taken_seconds": question.get("time_taken")
            }
            question_data_list.append(question_data)

        if question_data_list:
            questions_response = supabase_admin.table("quiz_questions").insert(question_data_list).execute()
            logger.info(f"Saved {len(question_data_list)} question results for attempt {attempt_id}")

        # Update mastery levels based on performance
        await update_mastery_levels(user_id, quiz_data, assessment_result)

        return True

    except Exception as e:
        logger.error(f"Error saving quiz attempt: {str(e)}")
        return False


async def update_mastery_levels(
    user_id: str,
    quiz_data: Dict[str, Any],
    assessment_result: Dict[str, Any]
):
    """
    Update user's mastery levels based on quiz performance
    """
    try:
        supabase_admin = get_supabase_admin()

        subject = quiz_data.get("subject", "General")
        topic = quiz_data.get("topic", "General")
        score_pct = assessment_result.get("percentage", 0.0) / 100.0  # Convert to 0-1 scale

        # Get existing mastery record
        existing = supabase_admin.table("mastery_levels")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("subject", subject)\
            .eq("topic", topic)\
            .execute()

        if existing.data:
            # Update existing mastery
            current = existing.data[0]
            current_score = current.get("mastery_score", 0.5)

            # Weighted average: 70% current, 30% new
            new_score = (current_score * 0.7) + (score_pct * 0.3)

            update_data = {
                "mastery_score": new_score,
                "is_mastered": new_score >= 0.8,
                "is_struggling": new_score < 0.5,
                "needs_revision": new_score < 0.7,
                "quizzes_attempted": (current.get("quizzes_attempted", 0) + 1),
                "quizzes_passed": (current.get("quizzes_passed", 0) + (1 if assessment_result.get("passed") else 0)),
                "avg_quiz_score": new_score,
                "last_practiced_at": datetime.utcnow().isoformat()
            }

            supabase_admin.table("mastery_levels")\
                .update(update_data)\
                .eq("user_id", user_id)\
                .eq("subject", subject)\
                .eq("topic", topic)\
                .execute()
        else:
            # Create new mastery record
            insert_data = {
                "user_id": user_id,
                "subject": subject,
                "topic": topic,
                "mastery_score": score_pct,
                "is_mastered": score_pct >= 0.8,
                "is_struggling": score_pct < 0.5,
                "needs_revision": score_pct < 0.7,
                "quizzes_attempted": 1,
                "quizzes_passed": 1 if assessment_result.get("passed") else 0,
                "avg_quiz_score": score_pct,
                "first_studied_at": datetime.utcnow().isoformat(),
                "last_practiced_at": datetime.utcnow().isoformat()
            }

            supabase_admin.table("mastery_levels").insert(insert_data).execute()

        logger.info(f"Updated mastery levels for {user_id} in {subject}/{topic}")

    except Exception as e:
        logger.error(f"Error updating mastery levels: {str(e)}")


async def get_quiz_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get user's recent quiz history

    Args:
        user_id: User ID
        limit: Number of recent attempts to retrieve

    Returns:
        List of quiz attempts
    """
    try:
        supabase_admin = get_supabase_admin()

        result = supabase_admin.table("quiz_attempts")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        return result.data if result.data else []

    except Exception as e:
        logger.error(f"Error fetching quiz history: {str(e)}")
        return []
