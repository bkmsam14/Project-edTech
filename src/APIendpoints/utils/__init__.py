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
    generate_quiz,
    fallback_quiz,
    generate_quiz_from_content,
    generate_quick_questions,
    calculate_quiz_score,
    generate_quiz_feedback
)
from utils.ai_utils import (
    call_local_model,
    call_local_model_with_context,
    generate_explanation_with_ai,
    generate_quiz_question_with_ai,
    is_ollama_available,
    get_available_models,
    call_local_model_mock,
    build_quiz_generation_prompt,
    generate_quiz_with_ai,
    build_explanation_prompt,
    build_text_simplification_prompt,
    _parse_quiz_json,
    _validate_quiz_structure,
    _validate_question_structure
)
from utils.recommendation import (
    generate_recommendations,
)

__all__ = [
    # Accessibility utilities
    "simplify_text",
    "break_long_sentences",
    "get_adaptation_css",
    "apply_accessibility_formatting",
    "break_into_sections",
    "add_visual_markers",
    # Quiz utilities
    "generate_quiz",
    "fallback_quiz",
    "generate_quiz_from_content",
    "generate_quick_questions",
    "calculate_quiz_score",
    "generate_quiz_feedback",
    # AI/LLM utilities
    "call_local_model",
    "call_local_model_with_context",
    "generate_explanation_with_ai",
    "generate_quiz_question_with_ai",
    "is_ollama_available",
    "get_available_models",
    "call_local_model_mock",
    # Structured prompt builders
    "build_quiz_generation_prompt",
    "generate_quiz_with_ai",
    "build_explanation_prompt",
    "build_text_simplification_prompt",
    # Recommendation utilities
    "generate_recommendations",
]
