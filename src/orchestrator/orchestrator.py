"""
Main Orchestrator Agent

Routes requests through the appropriate workflow pipeline.
This is the main traffic controller for the educational AI system.
"""

from typing import Dict, Any, Optional, Callable
import logging
from datetime import datetime

from .schemas import (
    Intent,
    WorkflowStep,
    OrchestratorRequest,
    OrchestratorResponse,
    WorkflowContext
)
from .intent_classifier import IntentClassifier
from .workflow_builder import WorkflowBuilder


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestration agent that routes educational AI requests
    through appropriate agent pipelines.
    """

    def __init__(
        self,
        step_handlers: Optional[Dict[WorkflowStep, Callable]] = None
    ):
        """
        Initialize orchestrator

        Args:
            step_handlers: Dictionary mapping workflow steps to handler functions.
                          Each handler should accept (context: WorkflowContext) and
                          return the result to be added to context.
        """
        self.intent_classifier = IntentClassifier()
        self.workflow_builder = WorkflowBuilder()
        self.step_handlers = step_handlers or {}

        logger.info("Orchestrator initialized")

    def register_step_handler(
        self,
        step: WorkflowStep,
        handler: Callable[[WorkflowContext], Any]
    ) -> None:
        """
        Register a handler for a workflow step

        Args:
            step: Workflow step to handle
            handler: Function that processes the step
        """
        self.step_handlers[step] = handler
        logger.info(f"Registered handler for step: {step.value}")

    async def process_request(
        self,
        request: OrchestratorRequest
    ) -> OrchestratorResponse:
        """
        Main entry point: process user request through workflow

        Args:
            request: User request to process

        Returns:
            Orchestrator response with results
        """
        logger.info(f"Processing request from user {request.user_id}")
        logger.info(f"Message: {request.message[:100]}...")

        # Step 1: Classify intent
        intent, confidence = self.intent_classifier.classify_with_confidence(
            request.message
        )
        logger.info(f"Detected intent: {intent.value} (confidence: {confidence:.2f})")

        # Handle unknown intent
        if intent == Intent.UNKNOWN:
            return OrchestratorResponse(
                success=False,
                intent=intent,
                data={},
                message="I'm not sure what you're asking. Could you rephrase?",
                errors=["Unable to determine user intent"]
            )

        # Step 2: Build workflow
        workflow = self.workflow_builder.build_workflow(intent)
        logger.info(f"Workflow: {[step.value for step in workflow]}")

        if not workflow:
            return OrchestratorResponse(
                success=False,
                intent=intent,
                data={},
                message="This request type is not yet supported.",
                errors=[f"No workflow defined for intent: {intent.value}"]
            )

        # Step 3: Initialize workflow context
        context = WorkflowContext(
            request=request,
            intent=intent
        )

        # Step 4: Execute workflow
        executed_steps = []

        for step in workflow:
            try:
                logger.info(f"Executing step: {step.value}")

                # Validate prerequisites
                if not self.workflow_builder.validate_step_prerequisites(step, context):
                    error_msg = f"Prerequisites not met for step: {step.value}"
                    logger.error(error_msg)
                    context.add_error(error_msg)
                    continue

                # Execute step
                result = await self._execute_step(step, context)

                # Store result in context
                context.add_result(step.value, result)
                executed_steps.append(step.value)

                logger.info(f"Step {step.value} completed successfully")

            except Exception as e:
                error_msg = f"Error executing step {step.value}: {str(e)}"
                logger.error(error_msg)
                context.add_error(error_msg)

                # Decide whether to continue or abort
                if self._is_critical_step(step):
                    logger.error("Critical step failed, aborting workflow")
                    break

        # Step 5: Build response
        response = self._build_response(context, executed_steps)

        logger.info(f"Request processing complete. Success: {response.success}")
        return response

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Any:
        """
        Execute a single workflow step

        Args:
            step: Workflow step to execute
            context: Current workflow context

        Returns:
            Result from step execution
        """
        # Check if handler is registered
        if step not in self.step_handlers:
            logger.warning(f"No handler registered for step: {step.value}")
            return {"status": "skipped", "reason": "no_handler"}

        # Execute handler
        handler = self.step_handlers[step]

        # Support both sync and async handlers
        if hasattr(handler, '__call__'):
            result = handler(context)
            # If result is awaitable, await it
            if hasattr(result, '__await__'):
                result = await result
            return result

        return None

    def _is_critical_step(self, step: WorkflowStep) -> bool:
        """
        Determine if a step is critical (failure should abort workflow)

        Args:
            step: Workflow step

        Returns:
            True if step is critical
        """
        critical_steps = {
            WorkflowStep.LOAD_PROFILE,
            WorkflowStep.RETRIEVE_LESSON,
        }
        return step in critical_steps

    def _build_response(
        self,
        context: WorkflowContext,
        executed_steps: list
    ) -> OrchestratorResponse:
        """
        Build final response from workflow context

        Args:
            context: Workflow context after execution
            executed_steps: List of successfully executed steps

        Returns:
            Orchestrator response
        """
        # Check for errors
        has_errors = context.has_errors()

        # Extract final data based on intent
        data = self._extract_response_data(context)

        # Generate message
        message = self._generate_response_message(context)

        return OrchestratorResponse(
            success=not has_errors,
            intent=context.intent,
            data=data,
            message=message,
            errors=context.errors,
            workflow_steps_executed=executed_steps
        )

    def _extract_response_data(self, context: WorkflowContext) -> Dict[str, Any]:
        """Extract relevant data for response based on intent"""
        data = {
            'intent': context.intent.value,
            'user_id': context.request.user_id
        }

        # Add intent-specific data
        if context.intent == Intent.EXPLAIN_LESSON:
            data['explanation'] = context.get_result(WorkflowStep.TUTOR_EXPLANATION.value)
            data['adapted_content'] = context.get_result(WorkflowStep.ADAPT_ACCESSIBILITY.value)

        elif context.intent == Intent.SIMPLIFY_CONTENT:
            data['simplified_content'] = context.get_result(WorkflowStep.ADAPT_ACCESSIBILITY.value)

        elif context.intent == Intent.GENERATE_QUIZ:
            data['quiz'] = context.get_result(WorkflowStep.GENERATE_QUIZ.value)

        elif context.intent == Intent.ASSESS_ANSWERS:
            data['assessment'] = context.get_result(WorkflowStep.ASSESS_QUIZ.value)
            data['recommendations'] = context.get_result(WorkflowStep.RECOMMEND.value)

        elif context.intent == Intent.RECOMMEND_NEXT:
            data['recommendations'] = context.get_result(WorkflowStep.RECOMMEND.value)

        elif context.intent in [Intent.SUMMARIZE_LESSON, Intent.ANSWER_QUESTION]:
            data['explanation'] = context.get_result(WorkflowStep.TUTOR_EXPLANATION.value)

        # Add profile and lesson info if available
        if context.user_profile:
            data['profile_loaded'] = True
            data['support_mode'] = context.user_profile.get('support_mode')

        if context.lesson_content:
            data['lesson_id'] = context.lesson_content.get('lesson_id')

        return data

    def _generate_response_message(self, context: WorkflowContext) -> str:
        """Generate human-readable response message"""
        if context.has_errors():
            return "I encountered some issues processing your request. Please try again."

        messages = {
            Intent.EXPLAIN_LESSON: "Here's an explanation of the lesson content.",
            Intent.SIMPLIFY_CONTENT: "I've simplified the content for easier understanding.",
            Intent.GENERATE_QUIZ: "Here's a quiz to test your understanding.",
            Intent.ASSESS_ANSWERS: "I've assessed your answers and provided feedback.",
            Intent.RECOMMEND_NEXT: "Here are my recommendations for what to learn next.",
            Intent.SUMMARIZE_LESSON: "Here's a summary of the key points.",
            Intent.ANSWER_QUESTION: "Here's the answer to your question.",
        }

        return messages.get(context.intent, "Request processed successfully.")

    def get_workflow_info(self, message: str) -> Dict[str, Any]:
        """
        Get workflow information without executing (useful for debugging)

        Args:
            message: User message

        Returns:
            Dictionary with workflow information
        """
        intent, confidence = self.intent_classifier.classify_with_confidence(message)
        workflow = self.workflow_builder.build_workflow(intent)

        return {
            'message': message,
            'intent': intent.value,
            'confidence': confidence,
            'workflow_steps': [step.value for step in workflow],
            'registered_handlers': [step.value for step in self.step_handlers.keys()]
        }
