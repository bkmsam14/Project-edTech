from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# Request Models
class ExplainRequest(BaseModel):
    """Request to explain a lesson"""
    user_id: str = Field(..., description="Unique user identifier")
    lesson_id: str = Field(..., description="Lesson to explain")
    message: str = Field(..., description="User's question or request")
    context: Optional[str] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student_123",
                "lesson_id": "biology_101",
                "message": "Can you explain photosynthesis?",
                "context": "We're studying plant biology"
            }
        }


class SimplifyRequest(BaseModel):
    """Request to simplify content"""
    user_id: str = Field(..., description="Unique user identifier")
    lesson_id: str = Field(..., description="Lesson to simplify")
    message: str = Field(..., description="Content to simplify")
    adaptation_type: Optional[str] = Field("dyslexia", description="Type of accessibility adaptation")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student_456",
                "lesson_id": "biology_101",
                "message": "Photosynthesis is the process...",
                "adaptation_type": "dyslexia"
            }
        }


class QuizRequest(BaseModel):
    """Request to generate a quiz"""
    user_id: str = Field(..., description="Unique user identifier")
    lesson_id: str = Field(..., description="Lesson to quiz on")
    course_id: Optional[str] = Field(None, description="Course ID for course-scoped quizzes")
    accessibility_mode: Optional[str] = Field(None, description="Accessibility mode")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    difficulty: str = Field("medium", description="Quiz difficulty level")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student_123",
                "lesson_id": "algebra_101",
                "num_questions": 5,
                "difficulty": "medium"
            }
        }


class AssessmentRequest(BaseModel):
    """Request to assess quiz answers"""
    user_id: str = Field(..., description="Unique user identifier")
    lesson_id: str = Field(..., description="Lesson being assessed")
    answers: Dict[str, str] = Field(..., description="Question IDs mapped to answers")
    quiz_id: Optional[str] = Field(None, description="Quiz ID if available")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student_123",
                "lesson_id": "algebra_101",
                "answers": {
                    "q1": "2x + 3 = 7",
                    "q2": "x = 2"
                },
                "quiz_id": "quiz_001"
            }
        }


class RecommendationRequest(BaseModel):
    """Request for learning recommendations"""
    user_id: str = Field(..., description="Unique user identifier")
    current_lesson_id: Optional[str] = Field(None, description="Current lesson being studied")
    depth: int = Field(1, ge=1, le=5, description="Number of recommendations to return")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student_123",
                "current_lesson_id": "algebra_101",
                "depth": 3
            }
        }


class QARequest(BaseModel):
    """Request for question answering"""
    user_id: str = Field(..., description="Unique user identifier")
    question: str = Field(..., description="Question to answer")
    lesson_id: Optional[str] = Field(None, description="Relevant lesson context")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student_123",
                "question": "What is photosynthesis?",
                "lesson_id": "biology_101"
            }
        }


# Response Models
class WorkflowStep(BaseModel):
    """Single workflow step execution"""
    step_name: str
    status: str = Field(..., description="Status of the step: pending, running, completed, failed")
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class BaseResponse(BaseModel):
    """Base response model for all endpoints"""
    success: bool
    intent: str
    message: str
    workflow_steps_executed: List[str]
    timestamp: Optional[str] = None
    user_id: Optional[str] = None


class ExplainResponse(BaseResponse):
    """Response for explanation requests"""
    data: Dict[str, Any] = Field({
        "explanation": {
            "content": "",
            "adapted_for": ""
        }
    })


class SimplifyResponse(BaseResponse):
    """Response for simplify requests"""
    data: Dict[str, Any] = Field({
        "simplified_content": "",
        "adaptation_type": ""
    })


class QuizResponse(BaseResponse):
    """Response for quiz generation"""
    data: Dict[str, Any] = Field({
        "quiz_id": "",
        "questions": [],
        "num_questions": 0
    })


class AssessmentResponse(BaseResponse):
    """Response for assessment"""
    data: Dict[str, Any] = Field({
        "score": 0,
        "percentage": 0,
        "feedback": [],
        "detailed_results": {}
    })


class RecommendationResponse(BaseResponse):
    """Response for recommendations"""
    data: Dict[str, Any] = Field({
        "recommendations": [],
        "reasoning": []
    })


class QAResponse(BaseResponse):
    """Response for Q&A"""
    data: Dict[str, Any] = Field({
        "answer": "",
        "sources": [],
        "confidence": 0.0
    })


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


# Re-export models from api_schemas for backward compatibility
from models.api_schemas import (
    ProfileCreateRequest,
    ProfileResponse,
    LessonUploadRequest,
    LessonResponse,
    LearnRequest,
    LearnResponse,
)
