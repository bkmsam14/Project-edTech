"""Quiz handler - GENERATE_QUIZ workflow step"""
import logging
import uuid
from utils.quiz_generator import generate_quiz_from_content, generate_quick_questions
from config import DEFAULT_NUM_QUIZ_QUESTIONS

logger = logging.getLogger(__name__)


async def generate_quiz_handler(context):
    """
    Generate quiz questions from lesson content.

    Input (from context):
        - context.request.message: User's message (may contain num_questions)
        - context.lesson_content: Lesson details
        - context.intermediate_results["retrieved_chunks"]: Content to base questions on
        - context.intermediate_results["adapted_content"]: Optionally use adapted content

    Output:
        - quiz_id: Unique quiz identifier
        - questions: List of quiz questions
        - lesson_id: Associated lesson
        - num_questions: Number of questions
        - stores in context.intermediate_results["quiz"]
    """
    try:
        # Parse request for number of questions and difficulty
        num_questions = DEFAULT_NUM_QUIZ_QUESTIONS
        difficulty = "medium"

        # Extract from request message if available
        message = context.request.message.lower()
        if "easy" in message:
            difficulty = "easy"
        elif "hard" in message:
            difficulty = "hard"

        # Get content for quiz generation
        content = ""
        if context.lesson_content:
            content = context.lesson_content.get("content", "")

        # Generate questions from content
        if content:
            questions = generate_quiz_from_content(content, num_questions, difficulty)
        else:
            # Fallback: generate generic questions
            lesson_title = context.lesson_content.get("title", "this topic") if context.lesson_content else "this topic"
            questions = generate_quick_questions(lesson_title, num_questions)

        # Create quiz object
        quiz_id = f"quiz_{context.request.lesson_id}_{uuid.uuid4().hex[:8]}"

        quiz_data = {
            "quiz_id": quiz_id,
            "lesson_id": context.request.lesson_id,
            "questions": questions,
            "num_questions": len(questions),
            "difficulty": difficulty,
            "created_timestamp": str(context.timestamp)
        }

        logger.info(f"Generated quiz {quiz_id} with {len(questions)} questions")

        return quiz_data

    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise
