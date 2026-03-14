"""
Data schemas for the Orchestrator Agent
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class Intent(Enum):
    """User intent types supported by the system"""
    EXPLAIN_LESSON = "explain_lesson"
    SIMPLIFY_CONTENT = "simplify_content"
    GENERATE_QUIZ = "generate_quiz"
    ASSESS_ANSWERS = "assess_answers"
    RECOMMEND_NEXT = "recommend_next"
    ANSWER_QUESTION = "answer_question"
    SUMMARIZE_LESSON = "summarize_lesson"
    UNKNOWN = "unknown"


class WorkflowStep(Enum):
    """Workflow steps that can be executed"""
    LOAD_PROFILE = "load_profile"
    RETRIEVE_LESSON = "retrieve_lesson"
    ADAPT_ACCESSIBILITY = "adapt_accessibility"
    TUTOR_EXPLANATION = "tutor_explanation"
    GENERATE_QUIZ = "generate_quiz"
    ASSESS_QUIZ = "assess_quiz"
    RECOMMEND = "recommend"
    VALIDATE_GUARDRAILS = "validate_guardrails"
    RETRIEVE_HISTORY = "retrieve_history"


@dataclass
class OrchestratorRequest:
    """Request to the orchestrator"""
    user_id: str
    message: str
    lesson_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowContext:
    """Context maintained throughout workflow execution"""
    request: OrchestratorRequest
    intent: Intent
    user_profile: Optional[Dict[str, Any]] = None
    lesson_content: Optional[Dict[str, Any]] = None
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    accessibility_adaptations: Optional[Dict[str, Any]] = None
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def add_result(self, step: str, result: Any) -> None:
        """Add intermediate result from a workflow step"""
        self.intermediate_results[step] = result

    def get_result(self, step: str) -> Optional[Any]:
        """Retrieve result from a previous workflow step"""
        return self.intermediate_results.get(step)

    def add_error(self, error: str) -> None:
        """Add error to context"""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if context has errors"""
        return len(self.errors) > 0


@dataclass
class OrchestratorResponse:
    """Response from the orchestrator"""
    success: bool
    intent: Intent
    data: Dict[str, Any]
    message: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    workflow_steps_executed: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'success': self.success,
            'intent': self.intent.value,
            'data': self.data,
            'message': self.message,
            'errors': self.errors,
            'workflow_steps_executed': self.workflow_steps_executed,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class UserProfile:
    """User profile schema"""
    user_id: str
    support_mode: str  # e.g., "dyslexia", "standard"
    preferences: Dict[str, Any] = field(default_factory=dict)
    learning_level: Optional[str] = None
    accessibility_settings: Dict[str, Any] = field(default_factory=dict)
    mastery_levels: Dict[str, float] = field(default_factory=dict)  # topic -> mastery score
