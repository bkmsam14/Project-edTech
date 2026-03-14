"""Quiz generation utilities"""
import logging
import uuid
from typing import List, Dict, Literal
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_quiz(context: str, topic: str, num_questions: int = 3) -> dict:
    """
    Generate a quiz from lesson context and topic.

    Questions are generated ONLY based on the provided lesson context.

    Args:
        context: Full lesson content/context
        topic: Topic or title of the quiz
        num_questions: Number of questions to generate (2-3 recommended)

    Returns:
        dict with structure:
        {
            "quiz_id": str,
            "topic": str,
            "questions": [
                {
                    "question_id": str,
                    "type": "mcq" or "true_false",
                    "question_text": str,
                    "options": list (for MCQ),
                    "correct_answer": str,
                    "concept_tag": str,
                    "difficulty": "easy" | "medium" | "hard"
                }
            ]
        }
    """
    # Limit to 2-3 questions
    num_questions = min(num_questions, 3)
    num_questions = max(num_questions, 2)

    # Create quiz ID
    quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"

    # Extract key sentences from context
    sentences = context.split('.')
    key_sentences = _extract_key_sentences(sentences, num_questions)

    questions = []

    # Generate mix of MCQ and True/False questions
    for i, sentence in enumerate(key_sentences[:num_questions]):
        # Alternate between MCQ and True/False
        question_type = "mcq" if i % 2 == 0 else "true_false"
        difficulty = _get_difficulty_for_index(i, num_questions)
        concept_tag = _extract_concept_tag(sentence, topic)

        question = _create_question(
            sentence=sentence,
            question_type=question_type,
            question_num=i + 1,
            difficulty=difficulty,
            concept_tag=concept_tag,
            context=context
        )

        if question:
            questions.append(question)

    quiz = {
        "quiz_id": quiz_id,
        "topic": topic,
        "questions": questions,
        "num_questions": len(questions),
        "created_at": datetime.utcnow().isoformat()
    }

    logger.info(f"Generated quiz {quiz_id} for topic '{topic}' with {len(questions)} questions")
    return quiz


def fallback_quiz(topic: str) -> dict:
    """
    Generate a fallback quiz with 2 simple questions.

    Used when:
    - Main quiz generation fails
    - No lesson context is available
    - Quick quiz needed without AI processing

    Returns the same structure as generate_quiz() but with generic questions.

    Args:
        topic: Topic or title of the quiz

    Returns:
        dict with structure:
        {
            "quiz_id": str,
            "topic": str,
            "questions": [
                {
                    "question_id": str,
                    "type": "true_false" or "short_answer",
                    "question_text": str,
                    "options": list (for true_false),
                    "correct_answer": str,
                    "concept_tag": str,
                    "difficulty": "easy" | "medium"
                }
            ]
        }
    """
    quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
    concept_tag = topic.lower().split()[0] if topic else "general"

    # Create 2 simple fallback questions
    questions = [
        {
            "question_id": "q1",
            "type": "true_false",
            "question_text": f"True or False: {topic} is an important concept to understand?",
            "options": ["True", "False"],
            "correct_answer": "True",
            "concept_tag": concept_tag,
            "difficulty": "easy"
        },
        {
            "question_id": "q2",
            "type": "short_answer",
            "question_text": f"In your own words, what is {topic} and why is it relevant?",
            "options": None,  # Short answer has no options
            "correct_answer": f"Any reasonable explanation of {topic}",
            "concept_tag": concept_tag,
            "difficulty": "medium"
        }
    ]

    quiz = {
        "quiz_id": quiz_id,
        "topic": topic,
        "questions": questions,
        "num_questions": len(questions),
        "created_at": datetime.utcnow().isoformat(),
        "is_fallback": True  # Flag indicating this is a fallback quiz
    }

    logger.warning(f"Generated FALLBACK quiz {quiz_id} for topic '{topic}' (main generation failed)")
    return quiz


def _extract_key_sentences(sentences: List[str], limit: int) -> List[str]:
    """Extract key sentences that can form good questions"""
    key_words = ["is", "are", "was", "were", "can", "could", "should", "would",
                 "defines", "includes", "involves", "requires", "means", "represents"]

    key_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 20:
            continue

        if any(kw in sentence.lower() for kw in key_words):
            key_sentences.append(sentence)
            if len(key_sentences) >= limit:
                break

    return key_sentences


def _get_difficulty_for_index(index: int, total: int) -> str:
    """Assign difficulty progression based on position"""
    if total <= 1:
        return "medium"
    elif total == 2:
        return "easy" if index == 0 else "medium"
    else:  # 3+
        if index == 0:
            return "easy"
        elif index == 1:
            return "medium"
        else:
            return "hard"


def _extract_concept_tag(sentence: str, topic: str) -> str:
    """Extract main concept from sentence for tagging"""
    # Simple approach: use topic or extract first noun phrase
    words = sentence.split()

    # Look for noun phrases (simplified)
    for i, word in enumerate(words):
        if word[0].isupper() and i > 0:  # Capitalized word (might be proper noun)
            return word.lower()

    # Fallback to topic
    return topic.lower().split()[0] if topic else "general"


def _create_question(
    sentence: str,
    question_type: Literal["mcq", "true_false"],
    question_num: int,
    difficulty: str,
    concept_tag: str,
    context: str
) -> Dict:
    """Create a single quiz question from sentence"""

    question_id = f"q{question_num}"

    if question_type == "mcq":
        question = _create_mcq_question(sentence, question_id, difficulty, concept_tag, context)
    else:  # true_false
        question = _create_true_false_question(sentence, question_id, difficulty, concept_tag, context)

    return question


def _create_mcq_question(sentence: str, q_id: str, difficulty: str,
                         concept_tag: str, context: str) -> Dict:
    """Create multiple choice question"""

    # Generate question text based on difficulty
    if difficulty == "easy":
        question_text = f"Which statement best describes: {sentence[:50]}...?"
        options = [
            "The statement is correct",
            "The statement is incorrect",
            "The statement is partially correct",
            "The statement is unclear"
        ]
    elif difficulty == "medium":
        question_text = f"Based on the lesson, what can we infer from: {sentence[:55]}...?"
        options = [
            "This implies a cause-and-effect relationship",
            "This is a definition",
            "This is a comparison",
            "This is a sequence of events"
        ]
    else:  # hard
        question_text = f"How does this concept apply: {sentence[:60]}...?"
        options = [
            "It provides foundational knowledge",
            "It challenges existing assumptions",
            "It demonstrates practical application",
            "It introduces a counter-example"
        ]

    return {
        "question_id": q_id,
        "type": "mcq",
        "question_text": question_text,
        "options": options,
        "correct_answer": options[0],
        "concept_tag": concept_tag,
        "difficulty": difficulty
    }


def _create_true_false_question(sentence: str, q_id: str, difficulty: str,
                                concept_tag: str, context: str) -> Dict:
    """Create true/false question"""

    # Generate statement based on difficulty
    if difficulty == "easy":
        question_text = f"True or False: {sentence[:70]}"
    elif difficulty == "medium":
        # Slightly modify the statement
        question_text = f"True or False: According to the lesson, {sentence.lower()[:70]}"
    else:  # hard
        # Create a more subtle statement
        question_text = f"True or False: The lesson suggests that {sentence.lower()[:65]}"

    return {
        "question_id": q_id,
        "type": "true_false",
        "question_text": question_text,
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept_tag": concept_tag,
        "difficulty": difficulty
    }


# ============= LEGACY FUNCTIONS (Kept for backward compatibility) =============

def generate_quiz_from_content(content: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
    """
    Generate quiz questions from lesson content.

    LEGACY: Use generate_quiz() instead for better structure.

    Args:
        content: Lesson content to base questions on
        num_questions: Number of questions to generate
        difficulty: Question difficulty (easy, medium, hard)

    Returns:
        List of quiz question dictionaries
    """
    quiz = generate_quiz(content, "General Topic", num_questions=num_questions)
    return quiz.get("questions", [])


def generate_quick_questions(lesson_title: str, num_questions: int = 3) -> List[Dict]:
    """
    Generate generic questions based on lesson title (fallback if content parsing fails).

    Args:
        lesson_title: Title of the lesson
        num_questions: Number of questions

    Returns:
        List of basic quiz questions
    """
    generic_questions = [
        {
            "id": "q1",
            "question": f"What is the main topic of this lesson about {lesson_title}?",
            "question_type": "short_answer",
            "difficulty": "easy"
        },
        {
            "id": "q2",
            "question": f"Can you describe the key concepts in {lesson_title}?",
            "question_type": "short_answer",
            "difficulty": "medium"
        },
        {
            "id": "q3",
            "question": f"How would you apply the knowledge from {lesson_title} to a real-world scenario?",
            "question_type": "short_answer",
            "difficulty": "hard"
        }
    ]

    return generic_questions[:num_questions]


def calculate_quiz_score(answers: Dict, quiz_questions: List[Dict]) -> float:
    """
    Calculate quiz score (simple grading).

    Args:
        answers: User's answers {question_id: answer_text}
        quiz_questions: List of quiz questions with correct answers

    Returns:
        Score as fraction (0.0 to 1.0)
    """
    if not quiz_questions:
        return 0.0

    correct_count = 0

    for question in quiz_questions:
        q_id = question.get("id") or question.get("question_id")
        if q_id in answers:
            user_answer = answers[q_id].lower().strip()
            correct_answer = question.get("correct_answer", "").lower().strip()

            # Simple matching
            if user_answer == correct_answer or correct_answer in user_answer:
                correct_count += 1

    return correct_count / len(quiz_questions)


def generate_quiz_feedback(answers: Dict, quiz_questions: List[Dict]) -> List[Dict]:
    """
    Generate feedback for each quiz answer.

    Args:
        answers: User's answers
        quiz_questions: Quiz questions with explanations

    Returns:
        List of feedback objects
    """
    feedback_list = []

    for question in quiz_questions:
        q_id = question.get("id") or question.get("question_id")
        user_answer = answers.get(q_id, "")
        correct_answer = question.get("correct_answer", "")
        question_text = question.get("question") or question.get("question_text", "")

        is_correct = user_answer.lower().strip() == correct_answer.lower().strip()

        feedback_list.append({
            "question_id": q_id,
            "question": question_text,
            "your_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "difficulty": question.get("difficulty", "medium")
        })

    return feedback_list
