"""Pydantic API Request and Response schemas for all endpoints"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ErrorResponse(BaseModel):
    detail: str


# --- Base response with shared fields ---

class BaseAPIResponse(BaseModel):
    success: bool
    intent: str
    message: str
    workflow_steps_executed: List[str]
    user_id: str
    timestamp: str
    data: Dict[str, Any]


# --- Explain ---

class ExplainRequest(BaseModel):
    user_id: str
    message: str
    lesson_id: Optional[str] = None
    context: Optional[str] = None


class ExplainResponse(BaseAPIResponse):
    pass


# --- Simplify ---

class SimplifyRequest(BaseModel):
    user_id: str
    message: str
    lesson_id: Optional[str] = None
    adaptation_type: str = "standard"


class SimplifyResponse(BaseAPIResponse):
    pass


# --- Quiz ---

class QuizRequest(BaseModel):
    user_id: str
    lesson_id: str
    accessibility_mode: Optional[str] = None
    difficulty: Optional[str] = "medium"
    num_questions: Optional[int] = 5


class QuizResponse(BaseAPIResponse):
    pass


# --- Assessment ---

class AssessmentRequest(BaseModel):
    user_id: str
    quiz_id: Optional[str] = None
    lesson_id: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    answers: Optional[Dict[str, Any]] = None
    accessibility_mode: Optional[str] = None


class AssessmentResponse(BaseAPIResponse):
    pass


# --- Recommendations ---

class RecommendationRequest(BaseModel):
    user_id: str
    current_lesson_id: Optional[str] = None
    depth: int = 3


class RecommendationResponse(BaseAPIResponse):
    pass


# --- Q&A ---

class QARequest(BaseModel):
    user_id: str
    question: str
    lesson_id: Optional[str] = None


class QAResponse(BaseAPIResponse):
    pass
