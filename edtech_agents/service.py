from __future__ import annotations

from .agents import assessment_agent, tutor_agent
from .models import AssessmentRequest, TutorRequest


class AgentValidationError(Exception):
    pass


def handle_tutor_request(payload: dict) -> dict:
    request = _parse_tutor_request(payload)
    result = tutor_agent(
        student_id=request.student_id,
        question=request.question,
        lesson_chunks=request.lesson_chunks,
        dyslexia_mode=request.dyslexia_mode,
        hints_used=request.hints_used,
    )
    return {
        "student_id": result["student_id"],
        "question": result["question"],
        "hints": result["hints"],
        "quiz": result["quiz"],
        "dyslexia_mode": result["dyslexia_mode"],
    }


def handle_assessment_request(payload: dict) -> dict:
    request = _parse_assessment_request(payload)
    result = assessment_agent(
        student_id=request.student_id,
        question_id=request.question_id,
        student_answer=request.student_answer,
        correct_answer=request.correct_answer,
        hints_used=request.hints_used,
        topic=request.topic,
    )
    return {
        "student_id": result["student_id"],
        "question_id": result["question_id"],
        "is_correct": result["is_correct"],
        "weakness_score": result["weakness_score"],
        "recommendation": result["recommendation"],
    }


def _parse_tutor_request(payload: dict) -> TutorRequest:
    try:
        return TutorRequest.from_dict(payload)
    except (ValueError, KeyError, TypeError) as exc:
        raise AgentValidationError(f"Invalid tutor request: {exc}") from exc


def _parse_assessment_request(payload: dict) -> AssessmentRequest:
    try:
        return AssessmentRequest.from_dict(payload)
    except (ValueError, KeyError, TypeError) as exc:
        raise AgentValidationError(f"Invalid assessment request: {exc}") from exc
