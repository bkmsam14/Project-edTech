"""Quiz generation utilities"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def generate_quiz_from_content(content: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
    """
    Generate quiz questions from lesson content.

    Args:
        content: Lesson content to base questions on
        num_questions: Number of questions to generate
        difficulty: Question difficulty (easy, medium, hard)

    Returns:
        List of quiz question dictionaries
    """
    questions = []

    # Extract key sentences (simple heuristic: sentences with keywords)
    sentences = content.split('. ')
    key_sentences = _extract_key_sentences(sentences, num_questions)

    for i, sentence in enumerate(key_sentences[:num_questions]):
        question = _create_question_from_sentence(sentence, difficulty, i + 1)
        if question:
            questions.append(question)

    logger.info(f"Generated {len(questions)} quiz questions")
    return questions


def _extract_key_sentences(sentences: List[str], limit: int) -> List[str]:
    """Extract key sentences that can form good questions"""
    key_words = ["is", "are", "was", "were", "can", "could", "should", "would", "defines", "includes"]

    key_sentences = []
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in key_words) and len(sentence) > 20:
            key_sentences.append(sentence.strip())
            if len(key_sentences) >= limit:
                break

    return key_sentences


def _create_question_from_sentence(sentence: str, difficulty: str, question_num: int) -> Dict:
    """Create a quiz question from a sentence"""

    # Simple strategy: extract subject and create fill-in-the-blank or multiple choice
    words = sentence.split()

    if len(words) < 5:
        return None

    if difficulty == "easy":
        question_text = f"Complete the sentence: {sentence[:50]}..."
        options = ["Correct answer", "Wrong option 1", "Wrong option 2", "Wrong option 3"]
    elif difficulty == "medium":
        question_text = f"According to the lesson: {sentence[:60]}...?"
        options = ["True", "False", "Partially true", "Not clear"]
    else:  # hard
        question_text = f"What is the relationship described: {sentence[:70]}...?"
        options = ["Cause and effect", "Definition", "Comparison", "Sequence"]

    return {
        "id": f"q{question_num}",
        "question": question_text,
        "question_type": "multiple_choice",
        "options": options,
        "correct_answer": options[0],
        "difficulty": difficulty,
        "explanation": f"The answer is '{options[0]}' because: {sentence}"
    }


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
        q_id = question.get("id")
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
        q_id = question.get("id")
        user_answer = answers.get(q_id, "")
        correct_answer = question.get("correct_answer", "")
        explanation = question.get("explanation", "")

        is_correct = user_answer.lower().strip() == correct_answer.lower().strip()

        feedback_list.append({
            "question_id": q_id,
            "question": question.get("question", ""),
            "your_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "feedback": explanation,
            "difficulty": question.get("difficulty", "medium")
        })

    return feedback_list
