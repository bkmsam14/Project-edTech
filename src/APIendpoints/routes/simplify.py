from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Project-edTech', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import SimplifyRequest, SimplifyResponse, ErrorResponse
from orchestrator.schemas import OrchestratorRequest

router = APIRouter()


@router.post("/simplify", response_model=SimplifyResponse, responses={400: {"model": ErrorResponse}})
async def simplify_content(request: SimplifyRequest):
    """
    Simplify educational content for accessibility.

    Adapts content based on the user's accessibility needs (dyslexia, etc).
    """
    try:
        from main import orchestrator

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message=f"Simplify this for {request.adaptation_type}: {request.message}",
            lesson_id=request.lesson_id
        )

        # Process through orchestrator
        orch_response = await orchestrator.process_request(orch_request)

        return SimplifyResponse(
            success=orch_response.success,
            intent="simplify_content",
            message=orch_response.message or "Content has been simplified for accessibility.",
            workflow_steps_executed=orch_response.workflow_steps_executed,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data=orch_response.data or {
                "simplified_content": request.message[:100],
                "adaptation_type": request.adaptation_type
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
