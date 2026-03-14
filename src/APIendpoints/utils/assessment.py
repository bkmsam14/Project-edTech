"""Assessment and quiz scoring utilities

Handles:
- Quiz scoring and grading
- Weak concept detection
- Mastery level computation
- Personalized feedback generation
"""
import logging
from typing import Dict, List, Any, Tuple
from config import MASTERY_THRESHOLD

logger = logging.getLogger(__name__)


def get_mastery_level(score: int, total: int) -> str:
    """
    Compute mastery level based on score and total.

    Args:
        score: Number of correct answers
        total: Total number of questions

    Returns:
        Mastery level: "high" (>=80%) | "medium" (50-79%) | "low" (<50%)
    """
    if total == 0:
        return "low"

    percentage = (score / total) * 100

    if percentage >= 80:
        return "high"
    elif percentage >= 50:
        return "medium"
    else:
        return "low"


def generate_feedback(mastery_level: str, weak_concepts: List[str]) -> str:
    """
    Generate encouraging feedback based on mastery level and weak concepts.

    Args:
        mastery_level: Level of mastery ("high", "medium", "low")
        weak_concepts: List of concepts the user struggled with

    Returns:
        Encouraging feedback string with suggestions
    """
    feedback = ""

    # Encouragement based on mastery level
    if mastery_level == "high":
        feedback = (
            "🎉 Excellent performance! You've demonstrated strong understanding of this material. "
        )
    elif mastery_level == "medium":
        feedback = (
            "👍 Good effort! You're making solid progress and understanding the key concepts. "
        )
    else:  # low
        feedback = (
            "💪 You're making a start! With more practice, you'll improve significantly. "
        )

    # Suggestions based on weak concepts
    if weak_concepts and mastery_level in ["low", "medium"]:
        concepts_str = ", ".join(weak_concepts)
        feedback += f"\n\n📚 Focus on reviewing these areas: {concepts_str}. "
        feedback += "Practice problems related to these topics to strengthen your understanding."
    elif mastery_level == "high":
        if weak_concepts:
            concepts_str = ", ".join(weak_concepts)
            feedback += f"\nYou might want to revisit {concepts_str} for even better mastery."
        else:
            feedback += "\nKeep up the great work and move forward to more challenging topics!"

    # Next steps
    if mastery_level == "high":
        feedback += (
            "\n\n→ Next Step: You're ready to advance. Consider moving on to the next lesson "
            "or trying a more challenging quiz."
        )
    else:
        feedback += (
            "\n\n→ Next Step: Review the material and practice more problems. You can retake this quiz anytime."
        )

    return feedback


def assess_quiz(quiz: Dict[str, Any], user_answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Comprehensive quiz assessment with scoring, weak concept detection, and feedback.

    This is the main assessment agent function that orchestrates the full assessment process.

    Args:
        quiz: Quiz object with structure:
            {
                "quiz_id": str,
                "topic": str,
                "questions": [
                    {
                        "question_id": str,
                        "question_text": str,
                        "correct_answer": str,
                        "concept_tag": str,
                        "difficulty": str,
                        ...
                    }
                ]
            }

        user_answers: Dict mapping question_id to user's answer
            {
                "q1": "Option A",
                "q2": "True",
                ...
            }

    Returns:
        Assessment dict with comprehensive results:
        {
            "quiz_id": str,
            "score": int,
            "total": int,
            "percentage": float (0-100),
            "mastery_level": "high" | "medium" | "low",
            "weak_concepts": [str],
            "strong_concepts": [str],
            "feedback": str,
            "detailed_feedback": [{"question_id": str, "is_correct": bool, "feedback": str}],
            "summary": str,
            "recommendations": [str]
        }
    """
    try:
        # Extract questions from quiz
        questions = quiz.get("questions", [])

        if not questions:
            logger.warning("No questions in quiz")
            return _create_empty_assessment(quiz)

        if not user_answers:
            logger.warning("No user answers provided")
            return _create_empty_assessment(quiz)

        # Step 1: Score the quiz
        score_result = _score_quiz(questions, user_answers)
        score = score_result["num_correct"]
        total = len(questions)
        percentage = score_result["percentage"]
        incorrect_questions = score_result["incorrect_questions"]

        # Step 2: Get mastery level
        mastery_level = get_mastery_level(score, total)

        # Step 3: Detect weak concepts
        weak_concepts = _detect_weak_concepts(incorrect_questions)
        strong_concepts = _detect_strong_concepts(questions, user_answers)

        # Step 4: Generate general feedback
        general_feedback = generate_feedback(mastery_level, weak_concepts)

        # Step 5: Generate detailed feedback
        detailed_feedback = _generate_detailed_feedback(questions, user_answers, incorrect_questions)

        # Step 6: Generate summary
        summary = _generate_summary(score, total, mastery_level)

        # Step 7: Generate recommendations
        recommendations = _generate_recommendations(weak_concepts, mastery_level, percentage)

        assessment = {
            "quiz_id": quiz.get("quiz_id"),
            "score": score,
            "total": total,
            "percentage": percentage,
            "mastery_level": mastery_level,
            "weak_concepts": weak_concepts,
            "strong_concepts": strong_concepts,
            "feedback": general_feedback,
            "detailed_feedback": detailed_feedback,
            "summary": summary,
            "recommendations": recommendations
        }

        logger.info(
            f"Assessment complete: {percentage:.1f}% ({score}/{total}), "
            f"Mastery: {mastery_level}, Weak concepts: {weak_concepts}"
        )

        return assessment

    except Exception as e:
        logger.error(f"Error assessing quiz: {e}")
        raise


def _score_quiz(questions: List[Dict], user_answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Score the quiz by comparing answers with correct answers.

    Args:
        questions: List of question objects
        user_answers: Dict of user's answers

    Returns:
        Dict with scoring results including:
        - num_correct: int
        - percentage: float (0-100)
        - incorrect_questions: list of incorrect question objects
    """
    num_correct = 0
    incorrect_questions = []

    for question in questions:
        q_id = question.get("question_id")
        user_answer = user_answers.get(q_id, "").lower().strip()
        correct_answer = question.get("correct_answer", "").lower().strip()

        # Compare answers
        is_correct = user_answer == correct_answer

        if is_correct:
            num_correct += 1
        else:
            incorrect_questions.append(question)

    total = len(questions)
    percentage = round((num_correct / total * 100), 1) if total > 0 else 0.0

    logger.debug(f"Quiz scoring: {num_correct}/{total} correct ({percentage}%)")

    return {
        "num_correct": num_correct,
        "percentage": percentage,
        "incorrect_questions": incorrect_questions
    }


def _detect_weak_concepts(incorrect_questions: List[Dict]) -> List[str]:
    """
    Detect weak concepts from incorrect questions.

    Args:
        incorrect_questions: List of questions the user got wrong

    Returns:
        List of concept_tags the user struggled with
    """
    weak_concepts = []

    for question in incorrect_questions:
        concept_tag = question.get("concept_tag", "unknown")
        if concept_tag not in weak_concepts:
            weak_concepts.append(concept_tag)

    logger.debug(f"Detected weak concepts: {weak_concepts}")
    return weak_concepts


def _detect_strong_concepts(questions: List[Dict], user_answers: Dict[str, str]) -> List[str]:
    """
    Detect strong concepts from correct questions.

    Args:
        questions: List of all questions
        user_answers: Dict of user's answers

    Returns:
        List of concept_tags the user mastered
    """
    correct_concepts = []

    for question in questions:
        q_id = question.get("question_id")
        user_answer = user_answers.get(q_id, "").lower().strip()
        correct_answer = question.get("correct_answer", "").lower().strip()

        # Check if answer is correct
        if user_answer == correct_answer:
            concept_tag = question.get("concept_tag", "unknown")
            if concept_tag not in correct_concepts:
                correct_concepts.append(concept_tag)

    logger.debug(f"Detected strong concepts: {correct_concepts}")
    return correct_concepts


def _generate_detailed_feedback(
    questions: List[Dict],
    user_answers: Dict[str, str],
    incorrect_questions: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Generate detailed feedback for each question.

    Args:
        questions: All questions
        user_answers: User's answers
        incorrect_questions: Questions user got wrong

    Returns:
        List of feedback objects for each question
    """
    feedback_list = []
    incorrect_ids = {q.get("question_id") for q in incorrect_questions}

    for question in questions:
        q_id = question.get("question_id")
        user_answer = user_answers.get(q_id, "")
        correct_answer = question.get("correct_answer", "")
        is_correct = q_id not in incorrect_ids

        # Generate feedback message
        if is_correct:
            feedback_msg = f"✓ Correct! You answered '{user_answer}'"
        else:
            feedback_msg = (
                f"✗ Incorrect. You answered '{user_answer}' but the correct answer is '{correct_answer}'. "
                f"This tests your understanding of {question.get('concept_tag', 'this concept')}."
            )

        feedback_list.append({
            "question_id": q_id,
            "question_text": question.get("question_text", ""),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "feedback": feedback_msg,
            "concept_tag": question.get("concept_tag"),
            "difficulty": question.get("difficulty")
        })

    return feedback_list


def _generate_summary(score: int, total: int, mastery_level: str) -> str:
    """
    Generate a summary message of the assessment.

    Args:
        score: Number of correct answers
        total: Total number of questions
        mastery_level: Computed mastery level

    Returns:
        Human-readable summary string
    """
    percentage = (score / total * 100) if total > 0 else 0

    if mastery_level == "high":
        return f"Excellent! You scored {score}/{total} ({percentage:.0f}%). You've demonstrated strong understanding."
    elif mastery_level == "medium":
        return f"Good job! You scored {score}/{total} ({percentage:.0f}%). You're on your way to mastery."
    else:  # low
        return f"You scored {score}/{total} ({percentage:.0f}%). Review the material and practice more."


def _generate_recommendations(
    weak_concepts: List[str],
    mastery_level: str,
    percentage: float
) -> List[str]:
    """
    Generate personalized learning recommendations.

    Args:
        weak_concepts: Concepts the user struggled with
        mastery_level: User's overall mastery level
        percentage: Quiz score percentage

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Recommendation 1: Address weak concepts
    if weak_concepts:
        concepts_str = ", ".join(weak_concepts)
        recommendations.append(
            f"Review and focus on these weak concepts: {concepts_str}. "
            f"Practice problems related to these topics."
        )

    # Recommendation 2: Based on mastery level
    if mastery_level == "low":
        recommendations.append(
            "Go back to the lesson material and study it carefully. "
            "Try simpler practice problems before attempting harder quizzes."
        )
    elif mastery_level == "medium":
        recommendations.append(
            "You're making progress! Continue practicing with medium difficulty problems. "
            "Try to understand the 'why' behind each concept."
        )
    else:  # high
        recommendations.append(
            "You've mastered this topic! Move on to the next lesson or try advanced challenges."
        )

    # Recommendation 3: Next steps
    if percentage >= 80:
        recommendations.append(
            f"Excellent preparation! Consider moving on to advanced topics in your learning path."
        )
    elif percentage >= 50:
        recommendations.append(
            f"You're making progress! Continue practicing to reach mastery."
        )
    else:
        recommendations.append(
            f"Try reviewing the material again and retake the quiz to improve."
        )

    return recommendations


def _create_empty_assessment(quiz: Dict[str, Any]) -> Dict[str, Any]:
    """Create an empty assessment (when no answers provided)"""
    return {
        "quiz_id": quiz.get("quiz_id"),
        "score": 0,
        "total": len(quiz.get("questions", [])),
        "percentage": 0.0,
        "mastery_level": "low",
        "weak_concepts": [],
        "strong_concepts": [],
        "feedback": "No assessment completed. Please answer the questions to receive feedback.",
        "detailed_feedback": [],
        "summary": "No assessment completed.",
        "recommendations": ["Complete the quiz to receive feedback."]
    }
