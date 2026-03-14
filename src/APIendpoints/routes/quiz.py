from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Project-edTech', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import QuizRequest, QuizResponse, ErrorResponse
from orchestrator.schemas import OrchestratorRequest

router = APIRouter()


@router.post("/quiz/generate", response_model=QuizResponse, responses={400: {"model": ErrorResponse}})
async def generate_quiz(request: QuizRequest):
    """
    Generate a quiz for a lesson.

    Creates quiz questions based on lesson content with specified difficulty.
    """
    try:
        from main import orchestrator

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message=f"Generate a {request.difficulty} quiz with {request.num_questions} questions",
            lesson_id=request.lesson_id
        )

        # Process through orchestrator
        orch_response = await orchestrator.process_request(orch_request)

        return QuizResponse(
            success=orch_response.success,
            intent="generate_quiz",
            message=orch_response.message or f"Generated {request.num_questions} quiz questions.",
            workflow_steps_executed=orch_response.workflow_steps_executed,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data=orch_response.data or {
                "quiz_id": f"quiz_{request.lesson_id}",
                "questions": [],
                "num_questions": request.num_questions
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
