from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Project-edTech', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import ExplainRequest, ExplainResponse, ErrorResponse
from orchestrator.schemas import OrchestratorRequest

router = APIRouter()


@router.post("/explain", response_model=ExplainResponse, responses={400: {"model": ErrorResponse}})
async def explain_lesson(request: ExplainRequest):
    """
    Explain a lesson to the user.

    Creates a detailed explanation adapted to the user's accessibility needs.
    """
    try:
        # Import orchestrator from main (avoid circular imports)
        from main import orchestrator

        # Create orchestrator request
        message = request.message
        if request.context:
            message += f"\n\nContext: {request.context}"

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message=request.message,
            lesson_id=request.lesson_id
        )

        # Process request through orchestrator
        orch_response = await orchestrator.process_request(orch_request)

        # Map orchestrator response to API response
        return ExplainResponse(
            success=orch_response.success,
            intent="explain_lesson",
            message=orch_response.message or "Here's an explanation of the lesson content.",
            workflow_steps_executed=orch_response.workflow_steps_executed,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data=orch_response.data or {
                "explanation": {
                    "content": "Unable to generate explanation",
                    "adapted_for": "dyslexia"
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

