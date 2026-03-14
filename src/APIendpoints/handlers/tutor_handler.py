"""Tutor handler - TUTOR_EXPLANATION workflow step"""
import logging

logger = logging.getLogger(__name__)


async def tutor_explanation_handler(context):
    """
    Generate educational explanation from lesson content.

    Uses rule-based text synthesis to create explanations from lesson chunks.

    Input (from context):
        - context.request.message: User's question/request
        - context.retrieved_chunks: Content chunks to base explanation on
        - context.user_profile: User profile (for personalization)

    Output:
        - explanation: Generated explanation text
        - sources: List of source chunks used
        - confidence: Confidence score
        - stores in context.intermediate_results["explanation"]
    """
    try:
        user_question = context.request.message
        chunks = context.retrieved_chunks or []

        if not chunks:
            logger.warning("No chunks available for explanation")
            return {
                "explanation": "I don't have enough content to explain this topic.",
                "sources": [],
                "confidence": 0.0
            }

        # Build explanation from chunks
        explanation_parts = [
            _create_introduction(user_question, context.lesson_content if context.lesson_content else {}),
        ]

        # Add chunk content
        for chunk in chunks[:3]:  # Use top 3 chunks
            explanation_parts.append(chunk.get("text", ""))

        # Add conclusion
        explanation_parts.append(_create_conclusion(context.lesson_content if context.lesson_content else {}))

        explanation = " ".join(explanation_parts)

        logger.info(f"Generated explanation using {len(chunks)} chunks")

        return {
            "explanation": explanation,
            "sources": [{"chunk_id": i, "relevance": chunk.get("relevance", 1.0)}
                       for i, chunk in enumerate(chunks[:3])],
            "confidence": 0.85  # Rule-based confidence
        }

    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise


def _create_introduction(question: str, lesson_content: dict) -> str:
    """Create introduction to explanation"""
    title = lesson_content.get("title", "this topic")
    return f"Let me explain {title}. Based on your question about '{question[:50]}...', here's what you need to know:"


def _create_conclusion(lesson_content: dict) -> str:
    """Create conclusion to explanation"""
    return "Does this help clarify the concept? Feel free to ask if you need more details or examples."
