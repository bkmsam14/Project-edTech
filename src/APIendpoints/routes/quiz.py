from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import QuizRequest, QuizResponse, ErrorResponse

router = APIRouter()


@router.post("/quiz/generate", response_model=QuizResponse, responses={400: {"model": ErrorResponse}})
async def generate_quiz(request: QuizRequest):
    """
    Generate a quiz for a lesson using the orchestrator pipeline.

    PART 8: Endpoint uses orchestrator.run_pipeline()
    """
    try:
        from main import orchestrator

        logger.info(f"📝 Generating quiz for lesson: {request.lesson_id}")

        # Get learner profile (mock for now - in production, load from database)
        profile = {
            "user_id": request.user_id,
            "name": f"User {request.user_id}",
            "support_mode": request.accessibility_mode or "standard"
        }

        # Lesson text (in production, retrieve from database)
        lesson_text = f"This is the lesson content for {request.lesson_id}. " * 50

        # PART 8: Call orchestrator.run_pipeline()
        logger.info("→ Calling orchestrator.run_pipeline()...")
        result = await orchestrator.run_pipeline(
            profile=profile,
            lesson_text=lesson_text,
            question=None
        )

        if not result.get("success"):
            logger.error(f"Pipeline failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Quiz generation failed")
            )

        quiz_data = result.get("quiz", {})
        logger.info(f"✓ Quiz generated with {len(quiz_data.get('questions', []))} questions")

        return QuizResponse(
            success=True,
            intent="generate_quiz",
            message=f"Generated quiz with {len(quiz_data.get('questions', []))} questions.",
            workflow_steps_executed=["profile", "retrieval", "accessibility", "tutor", "quiz"],
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "quiz_id": quiz_data.get("quiz_id", "quiz_001"),
                "topic": quiz_data.get("topic", "Learning Module"),
                "questions": quiz_data.get("questions", []),
                "num_questions": len(quiz_data.get("questions", [])),
                "difficulty": request.difficulty or "medium"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
