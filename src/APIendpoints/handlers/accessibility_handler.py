"""Accessibility handler - ADAPT_ACCESSIBILITY workflow step"""
import logging
from utils.accessibility import apply_accessibility_formatting, add_visual_markers

logger = logging.getLogger(__name__)


async def adapt_accessibility_handler(context):
    """
    Adapt content for accessibility needs (dyslexia support).

    Input (from context):
        - context.user_profile: User profile with support_mode
        - context.lesson_content or context.intermediate_results["lesson_content"]: Content to adapt
        - context.intermediate_results["retrieved_chunks"]: Content chunks to adapt

    Output:
        - adapted_content: Accessibility-formatted content
        - stores in context.intermediate_results["adapted_content"]
    """
    try:
        # Get user's support mode
        support_mode = "dyslexia"  # Default
        if context.user_profile:
            support_mode = context.user_profile.get("support_mode", "dyslexia")

        # Get content to adapt
        content_to_adapt = None

        if context.lesson_content:
            content_to_adapt = context.lesson_content.get("content", "")
        elif "lesson_content" in context.intermediate_results:
            lesson = context.intermediate_results["lesson_content"]
            content_to_adapt = lesson.get("content", "")

        if not content_to_adapt:
            logger.warning("No content to adapt")
            return {"adapted_content": "", "support_mode": support_mode}

        # Adapt content for accessibility
        adapted = apply_accessibility_formatting(content_to_adapt, support_mode)

        # Add visual markers for emphasis
        adapted["adapted_content"] = add_visual_markers(adapted["adapted_content"])

        # Also adapt the chunks if available
        if context.retrieved_chunks:
            adapted_chunks = []
            for chunk in context.retrieved_chunks:
                adapted_chunk = chunk.copy()
                adapted_chunk["text"] = apply_accessibility_formatting(
                    chunk.get("text", ""),
                    support_mode
                )["adapted_content"]
                adapted_chunks.append(adapted_chunk)
            adapted["adapted_chunks"] = adapted_chunks

        logger.info(f"Adapted content for {support_mode} support")
        return adapted

    except Exception as e:
        logger.error(f"Error adapting accessibility: {e}")
        raise
