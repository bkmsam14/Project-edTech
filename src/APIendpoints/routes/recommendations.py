from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Project-edTech', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import RecommendationRequest, RecommendationResponse, ErrorResponse
from orchestrator.schemas import OrchestratorRequest

router = APIRouter()


@router.post("/recommendations", response_model=RecommendationResponse, responses={400: {"model": ErrorResponse}})
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized learning recommendations.

    Returns recommended next topics based on user's learning history and current progress.
    """
    try:
        from main import orchestrator

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message="What should I learn next?",
            lesson_id=request.current_lesson_id or "",
            context={"depth": request.depth}
        )

        # Process through orchestrator
        orch_response = await orchestrator.process_request(orch_request)

        return RecommendationResponse(
            success=orch_response.success,
            intent="recommend_next",
            message=orch_response.message or f"Here are {request.depth} recommended topics for you.",
            workflow_steps_executed=orch_response.workflow_steps_executed,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data=orch_response.data or {
                "recommendations": [],
                "reasoning": [
                    "Based on your learning progress",
                    "Considering your current level",
                    "Aligned with prerequisites"
                ]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
