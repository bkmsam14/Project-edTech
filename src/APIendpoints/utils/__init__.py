"""Utility functions for the backend"""
from utils.accessibility import (
    simplify_text,
    break_long_sentences,
    get_adaptation_css,
    apply_accessibility_formatting,
    break_into_sections,
    add_visual_markers
)
from utils.quiz_generator import (
    generate_quiz_from_content,
    generate_quick_questions,
    calculate_quiz_score,
    generate_quiz_feedback
)

__all__ = [
    "simplify_text",
    "break_long_sentences",
    "get_adaptation_css",
    "apply_accessibility_formatting",
    "break_into_sections",
    "add_visual_markers",
    "generate_quiz_from_content",
    "generate_quick_questions",
    "calculate_quiz_score",
    "generate_quiz_feedback",
]
