from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import AssessmentRequest, AssessmentResponse, ErrorResponse
from utils.assessment import assess_quiz

router = APIRouter()


def _supabase_available() -> bool:
    return bool(os.getenv("SUPABASE_URL", "") and os.getenv("SUPABASE_SERVICE_KEY", ""))


@router.post("/assessment/submit", response_model=AssessmentResponse, responses={400: {"model": ErrorResponse}})
async def submit_assessment(request: AssessmentRequest):
    """Submit and grade quiz answers. Persists results to Supabase when configured."""
    try:
        logger.info(f"Assessing quiz for user: {request.user_id}")

        quiz = {
            "quiz_id": request.quiz_id or f"quiz_{datetime.utcnow().timestamp()}",
            "lesson_id": request.lesson_id,
            "topic": "Learning Module",
            "questions": request.questions or [],
            "completed_at": datetime.utcnow().isoformat(),
        }

        user_answers = request.answers or {}
        result = assess_quiz(quiz, user_answers)
        passed = result.get("percentage", 0) >= 80

        # Persist to Supabase (non-blocking, failures don't break the grading response)
        if _supabase_available() and request.user_id:
            try:
                import asyncio
                from handlers.quiz_storage_handler import save_quiz_attempt
                asyncio.create_task(
                    save_quiz_attempt(
                        user_id=request.user_id,
                        quiz_data=quiz,
                        answers=user_answers,
                        assessment_result={**result, "passed": passed},
                    )
                )
            except Exception as save_err:
                logger.warning(f"Quiz persistence skipped (non-fatal): {save_err}")

        logger.info(f"Assessment complete: {result.get('percentage', 0):.1f}% ({result.get('score', 0)}/{result.get('total', 0)})")

        return AssessmentResponse(
            success=True,
            intent="assess_answers",
            message=f"Assessment complete. Score: {result.get('percentage', 0):.1f}%",
            workflow_steps_executed=["assess_quiz"],
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "quiz_id": quiz["quiz_id"],
                "score": result.get("score", 0),
                "total": result.get("total", 0),
                "percentage": result.get("percentage", 0.0),
                "mastery_level": result.get("mastery_level", "low"),
                "weak_concepts": result.get("weak_concepts", []),
                "strong_concepts": result.get("strong_concepts", []),
                "feedback": result.get("feedback", ""),
                "detailed_feedback": result.get("detailed_feedback", []),
                "recommendations": result.get("recommendations", []),
                "passed": passed,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing quiz: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
