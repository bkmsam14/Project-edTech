from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Hint:
    level: int
    support_level: str
    text: str
    tts_text: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Hint":
        return cls(
            level=int(payload["level"]),
            support_level=str(payload["support_level"]),
            text=str(payload["text"]),
            tts_text=str(payload["tts_text"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "support_level": self.support_level,
            "text": self.text,
            "tts_text": self.tts_text,
        }


@dataclass(slots=True)
class QuizQuestion:
    type: str
    question: str
    correct_answer: str
    options: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "QuizQuestion":
        return cls(
            type=str(payload["type"]),
            question=str(payload["question"]),
            correct_answer=str(payload["correct_answer"]),
            options=[str(option) for option in payload.get("options", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "type": self.type,
            "question": self.question,
            "correct_answer": self.correct_answer,
        }
        if self.options:
            payload["options"] = self.options
        return payload


@dataclass(slots=True)
class Recommendation:
    next_action: str
    topic: str
    message: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Recommendation":
        return cls(
            next_action=str(payload["next_action"]),
            topic=str(payload["topic"]),
            message=str(payload["message"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "next_action": self.next_action,
            "topic": self.topic,
            "message": self.message,
        }


@dataclass(slots=True)
class TutorRequest:
    student_id: str
    question: str
    lesson_chunks: list[str]
    dyslexia_mode: bool = True
    hints_used: int = 0

    def __post_init__(self) -> None:
        if not self.student_id.strip():
            raise ValueError("student_id is required")
        if not self.question.strip():
            raise ValueError("question is required")
        if not self.lesson_chunks:
            raise ValueError("lesson_chunks must contain at least one chunk")
        if any(not str(chunk).strip() for chunk in self.lesson_chunks):
            raise ValueError("lesson_chunks must not contain empty values")
        self.lesson_chunks = [str(chunk).strip() for chunk in self.lesson_chunks]
        self.hints_used = max(0, int(self.hints_used))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TutorRequest":
        return cls(
            student_id=str(payload["student_id"]),
            question=str(payload["question"]),
            lesson_chunks=list(payload["lesson_chunks"]),
            dyslexia_mode=bool(payload.get("dyslexia_mode", True)),
            hints_used=int(payload.get("hints_used", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "student_id": self.student_id,
            "question": self.question,
            "lesson_chunks": self.lesson_chunks,
            "dyslexia_mode": self.dyslexia_mode,
            "hints_used": self.hints_used,
        }


@dataclass(slots=True)
class TutorResponse:
    student_id: str
    question: str
    hints: list[Hint]
    quiz: list[QuizQuestion]
    dyslexia_mode: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "student_id": self.student_id,
            "question": self.question,
            "hints": [hint.to_dict() for hint in self.hints],
            "quiz": [question.to_dict() for question in self.quiz],
            "dyslexia_mode": self.dyslexia_mode,
        }


@dataclass(slots=True)
class AssessmentRequest:
    student_id: str
    question_id: str
    student_answer: str
    correct_answer: str
    hints_used: int
    topic: str

    def __post_init__(self) -> None:
        if not self.student_id.strip():
            raise ValueError("student_id is required")
        if not self.question_id.strip():
            raise ValueError("question_id is required")
        if not self.correct_answer.strip():
            raise ValueError("correct_answer is required")
        if not self.topic.strip():
            raise ValueError("topic is required")
        self.hints_used = max(0, int(self.hints_used))
        self.student_answer = str(self.student_answer).strip()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AssessmentRequest":
        return cls(
            student_id=str(payload["student_id"]),
            question_id=str(payload["question_id"]),
            student_answer=str(payload.get("student_answer", "")),
            correct_answer=str(payload["correct_answer"]),
            hints_used=int(payload.get("hints_used", 0)),
            topic=str(payload["topic"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "student_id": self.student_id,
            "question_id": self.question_id,
            "student_answer": self.student_answer,
            "correct_answer": self.correct_answer,
            "hints_used": self.hints_used,
            "topic": self.topic,
        }


@dataclass(slots=True)
class AssessmentResponse:
    student_id: str
    question_id: str
    is_correct: bool
    weakness_score: float
    recommendation: Recommendation

    def to_dict(self) -> dict[str, Any]:
        return {
            "student_id": self.student_id,
            "question_id": self.question_id,
            "is_correct": self.is_correct,
            "weakness_score": self.weakness_score,
            "recommendation": self.recommendation.to_dict(),
        }
