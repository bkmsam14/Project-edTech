"""Profile and lesson management routes + unified learn workflow"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from datetime import datetime
from typing import Optional
import uuid
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import (
    ProfileCreateRequest, ProfileResponse,
    LessonUploadRequest, LessonResponse,
    LearnRequest, LearnResponse,
)
from orchestrator.schemas import OrchestratorRequest

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory stores (works without DB)
_profiles = {}
_lessons = {}


# --- Profile ---

@router.post("/profile", response_model=ProfileResponse)
async def create_profile(request: ProfileCreateRequest):
    """Create or update a learner profile."""
    user_id = request.user_id or f"user_{uuid.uuid4().hex[:8]}"

    profile = {
        "user_id": user_id,
        "name": request.name,
        "academic_level": request.academic_level,
        "support_mode": request.support_mode,
        "preferred_format": request.preferred_format,
        "accessibility_settings": {
            "font_size": f"{request.font_size}px",
            "line_spacing": str(request.line_spacing),
            "focus_mode": request.focus_mode,
            "font_family": "sans-serif",
            "letter_spacing": "0.1em",
        },
        "mastery_levels": {},
        "learning_level": request.academic_level,
        "created_at": datetime.utcnow().isoformat(),
    }

    _profiles[user_id] = profile
    logger.info(f"Profile created for user {user_id}")

    return ProfileResponse(success=True, profile=profile)


@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str):
    """Get a learner profile."""
    profile = _profiles.get(user_id)
    if not profile:
        # Return default profile
        profile = {
            "user_id": user_id,
            "name": "Student",
            "academic_level": "intermediate",
            "support_mode": "phonological",
            "preferred_format": "simplified",
            "accessibility_settings": {
                "font_size": "18px",
                "line_spacing": "1.8",
                "focus_mode": False,
                "font_family": "sans-serif",
            },
            "mastery_levels": {},
            "learning_level": "intermediate",
        }
    return ProfileResponse(success=True, profile=profile)


# --- Lesson ---

@router.post("/lesson", response_model=LessonResponse)
async def upload_lesson(request: LessonUploadRequest):
    """Upload lesson content."""
    lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"

    lesson = {
        "lesson_id": lesson_id,
        "title": request.title,
        "content": request.content,
        "subject": request.subject,
        "difficulty": request.difficulty,
        "created_at": datetime.utcnow().isoformat(),
    }

    _lessons[lesson_id] = lesson
    logger.info(f"Lesson uploaded: {lesson_id} ({request.title})")

    return LessonResponse(success=True, lesson=lesson)


@router.get("/lessons")
async def list_lessons():
    """List all available lessons."""
    return {"success": True, "lessons": list(_lessons.values())}


@router.get("/lesson/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: str):
    """Get a lesson by ID."""
    lesson = _lessons.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonResponse(success=True, lesson=lesson)


# --- File Upload with Parsing ---

@router.post("/lesson/upload-file", response_model=LessonResponse)
async def upload_lesson_file(
    file: UploadFile = File(...),
    user_id: str = Form("user_001"),
    subject: str = Form("General"),
    difficulty: str = Form("intermediate"),
    course_id: Optional[str] = Form(None),
):
    """Upload a file (pdf, docx, pptx, txt) and parse it into a lesson."""
    from utils.document_parser import parse_file

    file_bytes = await file.read()
    filename = file.filename or "untitled"

    try:
        text_content = parse_file(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text_content or len(text_content.strip()) < 20:
        raise HTTPException(status_code=400, detail="Could not extract meaningful text from file")

    title = filename.rsplit(".", 1)[0] if "." in filename else filename
    lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"
    document_id = f"moodle_course_{course_id}" if course_id else f"lesson_{lesson_id}"

    lesson = {
        "lesson_id": lesson_id,
        "title": title,
        "content": text_content,
        "subject": subject,
        "difficulty": difficulty,
        "document_id": document_id,
        "source_file": filename,
        "created_at": datetime.utcnow().isoformat(),
    }

    _lessons[lesson_id] = lesson
    logger.info(f"Lesson uploaded from file: {lesson_id} ({filename})")

    # Ingest into ChromaDB for RAG
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from src.mcp_moodle.ingest_moodle_content import ingest_text
        chunks_count = ingest_text(
            text=text_content,
            document_id=document_id,
            title=title,
            tenant_id="default",
        )
        logger.info(f"Ingested {chunks_count} chunks from uploaded file {filename}")
    except Exception as e:
        logger.warning(f"ChromaDB ingestion failed for {filename}: {e}")

    return LessonResponse(success=True, lesson=lesson)


# --- Unified Learn Workflow ---

@router.post("/learn", response_model=LearnResponse)
async def learn(request: LearnRequest):
    """
    Unified learning workflow endpoint.

    Runs the full pipeline:
    profile -> retrieval -> guardrails -> accessibility -> tutor -> response
    """
    try:
        from main import orchestrator

        logger.info(f"Learn request: intent={request.intent}, user={request.user_id}")

        # Map frontend intent strings to orchestrator message patterns
        intent_messages = {
            "explain": f"Explain this lesson: {request.question}",
            "summarize": f"Summarize this lesson: {request.question}",
            "simplify": f"Simplify this content: {request.question}",
            "quiz": f"Generate a quiz: {request.question}",
            "assess": f"Assess these answers: {request.question}",
            "recommend": f"What should I learn next? {request.question}",
            "qa": request.question,
        }

        message = intent_messages.get(request.intent, request.question)

        orch_request = OrchestratorRequest(
            user_id=request.user_id,
            message=message,
            lesson_id=request.lesson_id or "",
            context={
                "support_mode": request.support_mode,
                "preferred_format": request.preferred_format,
                "course_id": request.course_id,
                "document_id": (
                    request.document_id
                    or (f"moodle_course_{request.course_id}" if request.course_id else None)
                    or (f"lesson_{request.lesson_id}" if request.lesson_id else None)
                ),
            }
        )

        orch_response = await orchestrator.process_request(orch_request)
        data = orch_response.data or {}

        # Extract explanation text from various possible result shapes
        explanation = data.get("explanation")
        if isinstance(explanation, dict):
            explanation = explanation.get("explanation", str(explanation))

        adapted = data.get("adapted_content") or data.get("simplified_content")
        if isinstance(adapted, dict):
            adapted = adapted.get("adapted_text") or adapted.get("adapted_content") or adapted.get("content")
            if isinstance(adapted, dict):
                adapted = None

        return LearnResponse(
            success=orch_response.success,
            profile={"user_id": request.user_id, "support_mode": request.support_mode},
            lesson={"lesson_id": request.lesson_id} if request.lesson_id else None,
            retrieved_sources=[],
            explanation=explanation if isinstance(explanation, str) else str(explanation) if explanation else None,
            adapted_text=adapted if isinstance(adapted, str) else None,
            quiz=data.get("quiz") if isinstance(data.get("quiz"), dict) else None,
            assessment=data.get("assessment") if isinstance(data.get("assessment"), dict) else None,
            recommendation=data.get("recommendations") if isinstance(data.get("recommendations"), dict) else None,
            workflow_steps_executed=orch_response.workflow_steps_executed,
            errors=orch_response.errors,
        )

    except Exception as e:
        logger.error(f"Learn workflow error: {e}")
        return LearnResponse(
            success=False,
            errors=[str(e)],
        )
