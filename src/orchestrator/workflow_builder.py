"""
Workflow Builder

Defines which agents and steps to execute for each intent.
This is the "traffic controller" logic.
"""

from typing import List, Dict, Any, Callable
from .schemas import Intent, WorkflowStep, WorkflowContext


class WorkflowBuilder:
    """Builds execution workflows based on intent"""

    def __init__(self):
        """Initialize workflow builder with workflow definitions"""
        self.workflows: Dict[Intent, List[WorkflowStep]] = {
            Intent.EXPLAIN_LESSON: [
                WorkflowStep.LOAD_PROFILE,
                WorkflowStep.RETRIEVE_LESSON,
                WorkflowStep.ADAPT_ACCESSIBILITY,
                WorkflowStep.TUTOR_EXPLANATION,
                WorkflowStep.VALIDATE_GUARDRAILS,
            ],
            Intent.SIMPLIFY_CONTENT: [
                WorkflowStep.LOAD_PROFILE,
                WorkflowStep.RETRIEVE_LESSON,
                WorkflowStep.ADAPT_ACCESSIBILITY,
                WorkflowStep.VALIDATE_GUARDRAILS,
            ],
            Intent.GENERATE_QUIZ: [
                WorkflowStep.LOAD_PROFILE,
                WorkflowStep.RETRIEVE_LESSON,
                WorkflowStep.GENERATE_QUIZ,
                WorkflowStep.ADAPT_ACCESSIBILITY,
                WorkflowStep.VALIDATE_GUARDRAILS,
            ],
            Intent.ASSESS_ANSWERS: [
                WorkflowStep.LOAD_PROFILE,
                WorkflowStep.RETRIEVE_LESSON,
                WorkflowStep.ASSESS_QUIZ,
                WorkflowStep.RECOMMEND,
                WorkflowStep.VALIDATE_GUARDRAILS,
            ],
            Intent.RECOMMEND_NEXT: [
                WorkflowStep.LOAD_PROFILE,
                WorkflowStep.RETRIEVE_HISTORY,
                WorkflowStep.RECOMMEND,
                WorkflowStep.VALIDATE_GUARDRAILS,
            ],
            Intent.SUMMARIZE_LESSON: [
                WorkflowStep.LOAD_PROFILE,
                WorkflowStep.RETRIEVE_LESSON,
                WorkflowStep.TUTOR_EXPLANATION,
                WorkflowStep.ADAPT_ACCESSIBILITY,
                WorkflowStep.VALIDATE_GUARDRAILS,
            ],
            Intent.ANSWER_QUESTION: [
                WorkflowStep.LOAD_PROFILE,
                WorkflowStep.RETRIEVE_LESSON,
                WorkflowStep.TUTOR_EXPLANATION,
                WorkflowStep.ADAPT_ACCESSIBILITY,
                WorkflowStep.VALIDATE_GUARDRAILS,
            ],
        }

        # Define required context for each step
        self.step_requirements: Dict[WorkflowStep, List[str]] = {
            WorkflowStep.LOAD_PROFILE: [],  # No prerequisites
            WorkflowStep.RETRIEVE_LESSON: ['user_profile'],
            WorkflowStep.ADAPT_ACCESSIBILITY: ['user_profile', 'retrieved_chunks'],
            WorkflowStep.TUTOR_EXPLANATION: ['retrieved_chunks'],
            WorkflowStep.GENERATE_QUIZ: ['retrieved_chunks'],
            WorkflowStep.ASSESS_QUIZ: ['user_profile', 'lesson_content'],
            WorkflowStep.RECOMMEND: ['user_profile'],
            WorkflowStep.VALIDATE_GUARDRAILS: [],  # Can validate at any point
            WorkflowStep.RETRIEVE_HISTORY: ['user_profile'],
        }

    def build_workflow(self, intent: Intent) -> List[WorkflowStep]:
        """
        Build workflow for given intent

        Args:
            intent: Detected user intent

        Returns:
            List of workflow steps to execute in order
        """
        return self.workflows.get(intent, [])

    def get_required_context(self, step: WorkflowStep) -> List[str]:
        """
        Get required context attributes for a workflow step

        Args:
            step: Workflow step

        Returns:
            List of required context attribute names
        """
        return self.step_requirements.get(step, [])

    def validate_step_prerequisites(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> bool:
        """
        Check if all prerequisites for a step are satisfied

        Args:
            step: Workflow step to validate
            context: Current workflow context

        Returns:
            True if all prerequisites are met
        """
        required = self.get_required_context(step)

        for req in required:
            if not hasattr(context, req) or getattr(context, req) is None:
                return False

        return True

    def add_custom_workflow(
        self,
        intent: Intent,
        steps: List[WorkflowStep]
    ) -> None:
        """
        Add or override a workflow definition

        Args:
            intent: Intent to define workflow for
            steps: List of workflow steps
        """
        self.workflows[intent] = steps

    def get_workflow_description(self, intent: Intent) -> Dict[str, Any]:
        """
        Get human-readable workflow description

        Args:
            intent: Intent to describe

        Returns:
            Dictionary with workflow metadata
        """
        steps = self.build_workflow(intent)

        return {
            'intent': intent.value,
            'steps': [step.value for step in steps],
            'step_count': len(steps),
            'description': self._get_intent_description(intent)
        }

    def _get_intent_description(self, intent: Intent) -> str:
        """Get human-readable description of intent"""
        descriptions = {
            Intent.EXPLAIN_LESSON: "Provide detailed explanation of lesson content",
            Intent.SIMPLIFY_CONTENT: "Simplify and adapt content for accessibility",
            Intent.GENERATE_QUIZ: "Generate quiz based on lesson content",
            Intent.ASSESS_ANSWERS: "Assess student answers and provide feedback",
            Intent.RECOMMEND_NEXT: "Recommend next learning steps",
            Intent.SUMMARIZE_LESSON: "Provide concise summary of lesson",
            Intent.ANSWER_QUESTION: "Answer specific question about lesson",
            Intent.UNKNOWN: "Unable to determine intent"
        }
        return descriptions.get(intent, "Unknown intent")
