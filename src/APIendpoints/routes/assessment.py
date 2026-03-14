from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Project-edTech', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import AssessmentRequest, AssessmentResponse, ErrorResponse
from orchestrator.schemas import OrchestratorRequest

router = APIRouter()


@router.post("/assessment/submit", response_model=AssessmentResponse, responses={400: {"model": ErrorResponse}})
async def submit_assessment(request: AssessmentRequest):
    """
    Submit quiz answers for assessment and grading.

    Grades the submitted answers and provides detailed feedback.
    """
    try:
        from main import orchestrator

        answers_str = "\n".join([f"Q{k}: {v}" for k, v in request.answers.items()])

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message=f"Grade these answers:\n{answers_str}",
            lesson_id=request.lesson_id
        )

        # Store answers in context for handlers
        orch_request.context["answers"] = request.answers
        if request.quiz_id:
            orch_request.context["quiz_id"] = request.quiz_id

        # Process through orchestrator
        orch_response = await orchestrator.process_request(orch_request)

        return AssessmentResponse(
            success=orch_response.success,
            intent="assess_answers",
            message=orch_response.message or "Assessment complete.",
            workflow_steps_executed=orch_response.workflow_steps_executed,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data=orch_response.data or {
                "score": 0,
                "percentage": 0,
                "feedback": [],
                "detailed_results": {}
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
