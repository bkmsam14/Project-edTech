"""Handler registration and exports"""
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from handlers.profile_handler import load_profile_handler
from handlers.retrieval_handler import retrieve_lesson_handler, retrieve_history_handler
from handlers.accessibility_handler import adapt_accessibility_handler
from handlers.tutor_handler import tutor_explanation_handler
from handlers.quiz_handler import generate_quiz_handler
from handlers.assessment_handler import assess_quiz_handler
from handlers.recommendation_handler import recommendation_handler
from handlers.guardrails_handler import validate_guardrails_handler

logger = logging.getLogger(__name__)

# Map workflow steps to handlers
# This maps orchestrator.schemas.WorkflowStep to handler functions
WORKFLOW_HANDLERS = {
    "load_profile": load_profile_handler,
    "retrieve_lesson": retrieve_lesson_handler,
    "retrieve_history": retrieve_history_handler,
    "adapt_accessibility": adapt_accessibility_handler,
    "tutor_explanation": tutor_explanation_handler,
    "generate_quiz": generate_quiz_handler,
    "assess_quiz": assess_quiz_handler,
    "recommend": recommendation_handler,
    "validate_guardrails": validate_guardrails_handler,
}


def register_handlers(orchestrator):
    """
    Register all workflow handlers with the orchestrator.

    Args:
        orchestrator: Orchestrator instance to register handlers with
    """
    try:
        from orchestrator.schemas import WorkflowStep

        # Create handler mappings using WorkflowStep enum
        step_to_handler = {
            WorkflowStep.LOAD_PROFILE: load_profile_handler,
            WorkflowStep.RETRIEVE_LESSON: retrieve_lesson_handler,
            WorkflowStep.RETRIEVE_HISTORY: retrieve_history_handler,
            WorkflowStep.ADAPT_ACCESSIBILITY: adapt_accessibility_handler,
            WorkflowStep.TUTOR_EXPLANATION: tutor_explanation_handler,
            WorkflowStep.GENERATE_QUIZ: generate_quiz_handler,
            WorkflowStep.ASSESS_QUIZ: assess_quiz_handler,
            WorkflowStep.RECOMMEND: recommendation_handler,
            WorkflowStep.VALIDATE_GUARDRAILS: validate_guardrails_handler,
        }

        # Register each handler
        for step, handler in step_to_handler.items():
            orchestrator.register_step_handler(step, handler)
            logger.info(f"Registered handler for {step.value}")

        logger.info(f"Successfully registered {len(step_to_handler)} handlers")

    except Exception as e:
        logger.error(f"Error registering handlers: {e}")
        raise


__all__ = [
    "register_handlers",
    "load_profile_handler",
    "retrieve_lesson_handler",
    "retrieve_history_handler",
    "adapt_accessibility_handler",
    "tutor_explanation_handler",
    "generate_quiz_handler",
    "assess_quiz_handler",
    "recommendation_handler",
    "validate_guardrails_handler",
]
