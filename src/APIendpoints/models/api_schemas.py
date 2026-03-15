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
    course_id: Optional[str] = None
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


# --- Profile Management ---

class ProfileCreateRequest(BaseModel):
    user_id: Optional[str] = None
    name: str = "Student"
    academic_level: str = "intermediate"
    support_mode: str = "phonological"
    preferred_format: str = "simplified"
    font_size: int = 18
    line_spacing: float = 1.8
    focus_mode: bool = False


class ProfileResponse(BaseModel):
    success: bool
    profile: Dict[str, Any]


# --- Lesson Upload ---

class LessonUploadRequest(BaseModel):
    user_id: str
    title: str
    content: str
    subject: Optional[str] = "General"
    difficulty: Optional[str] = "intermediate"


class LessonResponse(BaseModel):
    success: bool
    lesson: Dict[str, Any]


# --- Unified Learn Workflow ---

class LearnRequest(BaseModel):
    user_id: str
    lesson_id: Optional[str] = None
    course_id: Optional[str] = None
    document_id: Optional[str] = None
    question: str
    intent: str = "explain"
    support_mode: str = "phonological"
    preferred_format: str = "simplified_text"


class LearnResponse(BaseModel):
    success: bool
    profile: Optional[Dict[str, Any]] = None
    lesson: Optional[Dict[str, Any]] = None
    retrieved_sources: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    adapted_text: Optional[str] = None
    quiz: Optional[Dict[str, Any]] = None
    assessment: Optional[Dict[str, Any]] = None
    recommendation: Optional[Dict[str, Any]] = None
    workflow_steps_executed: List[str] = []
    errors: List[str] = []
