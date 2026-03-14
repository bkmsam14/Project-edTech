"""Quiz handler - GENERATE_QUIZ workflow step"""
import logging
import uuid
from utils.quiz_generator import fallback_quiz
from utils.ai_utils import generate_quiz_with_ai, is_ollama_available
from config import DEFAULT_NUM_QUIZ_QUESTIONS

logger = logging.getLogger(__name__)


async def generate_quiz_handler(context):
    """
    Generate quiz questions from lesson content.

    Intelligently selects between:
    - AI-powered quiz (if Ollama available and context sufficient)
    - Rule-based quiz
    - Simple fallback quiz

    Workflow:
    1. Try AI generation if Ollama available and content sufficient
    2. Fall back to rule-based generation
    3. Fall back to simple fallback quiz

    This handler ALWAYS returns a valid quiz.

    Input (from context):
        - context.request.message: User's message (may contain num_questions)
        - context.lesson_content: Lesson details
        - context.intermediate_results["retrieved_chunks"]: Content chunks

    Output:
        - quiz_id: Unique quiz identifier
        - topic: Quiz topic
        - questions: List of quiz questions
        - num_questions: Number of questions
        - source: "ai" | "rule_based" | "fallback"
        - is_fallback: Boolean indicating if fallback was used
        - stores in context.intermediate_results["quiz"]
    """
    try:
        # Parse request parameters
        num_questions = DEFAULT_NUM_QUIZ_QUESTIONS
        difficulty = "easy"
        topic = "General Topic"

        # Extract from request message if available
        message = context.request.message.lower()
        if "easy" in message:
            difficulty = "easy"
        elif "hard" in message:
            difficulty = "hard"
        else:
            difficulty = "medium"

        # Get topic from lesson or context
        if context.lesson_content:
            topic = context.lesson_content.get("title", topic)
            content = context.lesson_content.get("content", "")
        else:
            content = ""

        # Initialize quiz_data
        quiz_data = None
        source = "fallback"

        # Strategy 1: Try AI generation if available and content is sufficient
        if is_ollama_available() and content and len(content) > 100:
            try:
                logger.info("Strategy 1: Attempting AI-powered quiz generation")
                quiz_data = generate_quiz_with_ai(
                    lesson_context=content,
                    topic=topic,
                    num_questions=num_questions,
                    difficulty=difficulty,
                    for_dyslexic_learners=True
                )

                # Verify AI returned valid quiz (not fallback)
                if quiz_data and not quiz_data.get("is_fallback", False):
                    source = "ai"
                    logger.info(f"Successfully generated AI quiz with {len(quiz_data.get('questions', []))} questions")
                else:
                    logger.warning("AI did not return valid quiz, trying fallback")
                    quiz_data = None

            except Exception as e:
                logger.warning(f"AI strategy failed: {e}. Trying fallback.")
                quiz_data = None

        # Strategy 2: If AI failed, use fallback
        if not quiz_data:
            logger.info("Strategy 2: Using fallback quiz generation")
            quiz_data = fallback_quiz(topic=topic)
            source = "fallback"

        # Ensure quiz has required fields
        if not quiz_data:
            logger.error("All quiz generation strategies failed!")
            # Last resort: create minimal valid quiz
            quiz_data = fallback_quiz(topic)
            source = "fallback"

        # Enrich with handler metadata
        quiz_data["source"] = source
        quiz_data["lesson_id"] = context.request.lesson_id
        quiz_data["difficulty"] = difficulty
        quiz_data["handler"] = "generate_quiz_handler"

        logger.info(
            f"Generated quiz {quiz_data.get('quiz_id')} with {len(quiz_data.get('questions', []))} questions "
            f"(source: {source})"
        )

        return quiz_data

    except Exception as e:
        logger.error(f"Unhandled error in quiz handler: {e}")
        # Ensure we always return a valid quiz
        logger.info("Returning minimal fallback quiz due to handler error")
        return {
            "quiz_id": f"quiz_error_{uuid.uuid4().hex[:8]}",
            "topic": "Error Recovery",
            "questions": [
                {
                    "question_id": "q1",
                    "type": "true_false",
                    "question_text": "This is a placeholder question due to a generation error.",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "concept_tag": "general",
                    "difficulty": "easy"
                }
            ],
            "num_questions": 1,
            "source": "error_fallback",
            "is_fallback": True,
            "error": str(e),
            "lesson_id": context.request.lesson_id if hasattr(context.request, 'lesson_id') else "unknown"
        }
