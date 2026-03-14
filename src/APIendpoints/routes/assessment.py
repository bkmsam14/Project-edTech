from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import AssessmentRequest, AssessmentResponse, ErrorResponse

router = APIRouter()


@router.post("/assessment/submit", response_model=AssessmentResponse, responses={400: {"model": ErrorResponse}})
async def submit_assessment(request: AssessmentRequest):
    """
    Submit and grade quiz answers using the orchestrator assessment pipeline.

    PART 8: Endpoint uses orchestrator.assess_quiz_answers()
    """
    try:
        from main import orchestrator

        logger.info(f"📊 Assessing quiz for user: {request.user_id}")

        # Get learner profile (mock for now)
        profile = {
            "user_id": request.user_id,
            "name": f"User {request.user_id}",
            "support_mode": request.accessibility_mode or "standard"
        }

        # Build quiz object (in production, load from database)
        quiz = {
            "quiz_id": request.quiz_id or "quiz_001",
            "lesson_id": request.lesson_id,
            "topic": "Learning Module",
            "questions": request.questions or []
        }

        # Convert answers to proper format
        user_answers = request.answers or {}

        # PART 8: Call orchestrator.assess_quiz_answers()
        logger.info("→ Calling orchestrator.assess_quiz_answers()...")
        result = await orchestrator.assess_quiz_answers(
            quiz=quiz,
            user_answers=user_answers,
            user_profile=profile
        )

        if not result.get("success"):
            logger.error(f"Assessment failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Assessment failed")
            )

        logger.info(
            f"✓ Assessment complete: {result.get('percentage', 0):.1f}% "
            f"({result.get('score', 0)}/{result.get('total', 0)})"
        )

        return AssessmentResponse(
            success=True,
            intent="assess_answers",
            message=f"Assessment complete. Score: {result.get('percentage', 0):.1f}%",
            workflow_steps_executed=["assessment"],
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "quiz_id": quiz.get("quiz_id"),
                "score": result.get("score", 0),
                "total": result.get("total", 0),
                "percentage": result.get("percentage", 0.0),
                "mastery_level": result.get("mastery_level", "low"),
                "weak_concepts": result.get("weak_concepts", []),
                "strong_concepts": result.get("strong_concepts", []),
                "feedback": result.get("feedback", ""),
                "detailed_feedback": result.get("detailed_feedback", []),
                "recommendations": result.get("recommendations", []),
                "passed": result.get("passed", False)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error assessing quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
