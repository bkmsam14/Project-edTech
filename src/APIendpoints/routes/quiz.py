from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import sys
import os
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import QuizRequest, QuizResponse, ErrorResponse
from orchestrator.schemas import OrchestratorRequest

router = APIRouter()


def _supabase_available() -> bool:
    return bool(os.getenv("SUPABASE_URL", "") and os.getenv("SUPABASE_SERVICE_KEY", ""))


@router.post("/quiz/generate", response_model=QuizResponse, responses={400: {"model": ErrorResponse}})
async def generate_quiz(request: QuizRequest):
    """Generate a personalized quiz using the orchestrator pipeline."""
    try:
        from main import orchestrator

        logger.info(f"Generating quiz for lesson: {request.lesson_id}, user: {request.user_id}")

        # Build base context
        context = {
            "num_questions": request.num_questions or 5,
            "difficulty": request.difficulty or "medium",
            "accessibility_mode": request.accessibility_mode or "standard",
            "course_id": request.course_id,
            "document_id": f"moodle_course_{request.course_id}" if request.course_id else None,
        }

        # Inject personalization context when Supabase is available
        if _supabase_available() and request.user_id:
            try:
                from handlers.personalization_handler import get_personalized_quiz_config, format_learning_context_for_prompt
                quiz_config = await get_personalized_quiz_config(request.user_id)
                learning_context_prompt = await format_learning_context_for_prompt(request.user_id)

                # Override with personalized settings if not manually set
                context["difficulty"] = request.difficulty or quiz_config.get("difficulty", "medium")
                context["num_questions"] = request.num_questions or quiz_config.get("num_questions", 5)
                context["quiz_type"] = quiz_config.get("quiz_type", "practice")
                context["focus_topics"] = quiz_config.get("focus_topics", [])
                context["learning_context"] = learning_context_prompt

                logger.info(
                    f"Personalized quiz: difficulty={context['difficulty']}, "
                    f"questions={context['num_questions']}, "
                    f"focus={context['focus_topics']}"
                )
            except Exception as pe:
                logger.warning(f"Personalization skipped (non-fatal): {pe}")

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message=f"Generate a {context['difficulty']} quiz for this lesson",
            lesson_id=request.lesson_id,
            context=context,
        )

        orch_response = await orchestrator.process_request(orch_request)
        quiz_data = orch_response.data.get("quiz") or {}

        return QuizResponse(
            success=orch_response.success,
            intent="generate_quiz",
            message=orch_response.message or "Here's a quiz to test your understanding.",
            workflow_steps_executed=orch_response.workflow_steps_executed,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "quiz_id": quiz_data.get("quiz_id", "quiz_001"),
                "topic": quiz_data.get("topic", request.lesson_id),
                "questions": quiz_data.get("questions", []),
                "num_questions": len(quiz_data.get("questions", [])),
                "difficulty": context["difficulty"],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
