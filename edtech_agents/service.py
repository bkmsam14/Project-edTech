from __future__ import annotations

from .agents import assessment_agent, tutor_agent
from .models import (
    AssessmentRequest,
    AssessmentResponse,
    Hint,
    QuizQuestion,
    Recommendation,
    TutorRequest,
    TutorResponse,
)


class AgentValidationError(ValueError):
    pass


def handle_tutor_request(payload: dict) -> dict:
    request = _parse_tutor_request(payload)
    response = tutor_agent(
        student_id=request.student_id,
        question=request.question,
        lesson_chunks=request.lesson_chunks,
        dyslexia_mode=request.dyslexia_mode,
        hints_used=request.hints_used,
    )
    typed_response = TutorResponse(
        student_id=response["student_id"],
        question=response["question"],
        hints=[Hint.from_dict(item) for item in response["hints"]],
        quiz=[QuizQuestion.from_dict(item) for item in response["quiz"]],
        dyslexia_mode=bool(response["dyslexia_mode"]),
    )
    return typed_response.to_dict()


def handle_assessment_request(payload: dict) -> dict:
    request = _parse_assessment_request(payload)
    response = assessment_agent(
        student_id=request.student_id,
        question_id=request.question_id,
        student_answer=request.student_answer,
        correct_answer=request.correct_answer,
        hints_used=request.hints_used,
        topic=request.topic,
    )
    typed_response = AssessmentResponse(
        student_id=response["student_id"],
        question_id=response["question_id"],
        is_correct=bool(response["is_correct"]),
        weakness_score=float(response["weakness_score"]),
        recommendation=Recommendation.from_dict(response["recommendation"]),
    )
    return typed_response.to_dict()


def _parse_tutor_request(payload: dict) -> TutorRequest:
    try:
        return TutorRequest.from_dict(payload)
    except (KeyError, TypeError, ValueError) as error:
        raise AgentValidationError(f"Invalid tutor request: {error}") from error


def _parse_assessment_request(payload: dict) -> AssessmentRequest:
    try:
        return AssessmentRequest.from_dict(payload)
    except (KeyError, TypeError, ValueError) as error:
        raise AgentValidationError(f"Invalid assessment request: {error}") from error