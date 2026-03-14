from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Project-edTech', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import QARequest, QAResponse, ErrorResponse
from orchestrator.schemas import OrchestratorRequest

router = APIRouter()


@router.post("/qa", response_model=QAResponse, responses={400: {"model": ErrorResponse}})
async def answer_question(request: QARequest):
    """
    Answer a user's question about a lesson.

    Provides an answer based on lesson content with source references.
    """
    try:
        from main import orchestrator

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message=request.question,
            lesson_id=request.lesson_id or ""
        )

        # Process through orchestrator
        orch_response = await orchestrator.process_request(orch_request)

        return QAResponse(
            success=orch_response.success,
            intent="answer_question",
            message=orch_response.message or "Here's the answer to your question.",
            workflow_steps_executed=orch_response.workflow_steps_executed,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data=orch_response.data or {
                "answer": f"Answer to: {request.question}",
                "sources": [
                    {
                        "lesson_id": request.lesson_id or "general",
                        "section": "Main Content",
                        "relevance": 0.95
                    }
                ],
                "confidence": 0.85
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
