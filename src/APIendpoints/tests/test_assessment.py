"""
Unit tests for the Assessment Agent

Tests mock quiz data and the assess_quiz() function.
Manual testing for verifying quiz and assessment agents.
"""

import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.assessment import assess_quiz, get_mastery_level, generate_feedback


# ============================================================================
# MOCK DATA: Sample Lesson Context
# ============================================================================

PHOTOSYNTHESIS_LESSON = {
    "lesson_id": "lesson_001",
    "title": "Photosynthesis: The Process of Life",
    "content": """
    Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide
    to produce oxygen and energy in the form of glucose. This process occurs primarily in
    the leaves of plants, specifically in the chloroplasts.
    
    There are two main stages of photosynthesis:
    
    1. Light-Dependent Reactions (Light Reactions)
       - Occur in the thylakoid membranes of chloroplasts
       - Require sunlight energy
       - Produce ATP and NADPH
       - Release oxygen as a byproduct
    
    2. Light-Independent Reactions (Calvin Cycle)
       - Occur in the stroma of chloroplasts
       - Do not directly require light
       - Use ATP and NADPH from light reactions
       - Produce glucose (C6H12O6)
    
    The simplified equation for photosynthesis is:
    6CO2 + 6H2O + light energy → C6H12O6 + 6O2
    
    Key molecules:
    - Chlorophyll: The pigment that captures light energy (green color)
    - ATP: Energy currency of the cell
    - NADPH: Electron carrier molecule
    - RuBisCO: Enzyme that fixes CO2
    """,
    "concepts": ["photosynthesis", "light_reactions", "calvin_cycle", "chlorophyll", "glucose"]
}


# ============================================================================
# MOCK DATA: Sample Generated Quiz
# ============================================================================

PHOTOSYNTHESIS_QUIZ = {
    "quiz_id": "quiz_001",
    "topic": "Photosynthesis",
    "difficulty": "intermediate",
    "questions": [
        {
            "question_id": "q1",
            "question_text": "What is the main function of photosynthesis?",
            "correct_answer": "to convert light energy into chemical energy stored in glucose",
            "options": [
                "To release carbon dioxide",
                "To convert light energy into chemical energy stored in glucose",
                "To break down glucose for energy",
                "To absorb water from the soil"
            ],
            "question_type": "multiple_choice",
            "concept_tag": "photosynthesis",
            "difficulty": "easy"
        },
        {
            "question_id": "q2",
            "question_text": "In which part of the chloroplast do the light-dependent reactions occur?",
            "correct_answer": "thylakoid membranes",
            "options": [
                "Stroma",
                "Thylakoid membranes",
                "Outer membrane",
                "Matrix"
            ],
            "question_type": "multiple_choice",
            "concept_tag": "light_reactions",
            "difficulty": "medium"
        },
        {
            "question_id": "q3",
            "question_text": "The Calvin Cycle directly requires light energy to function.",
            "correct_answer": "false",
            "options": ["True", "False"],
            "question_type": "true_false",
            "concept_tag": "calvin_cycle",
            "difficulty": "medium"
        },
        {
            "question_id": "q4",
            "question_text": "What is chlorophyll's primary role in photosynthesis?",
            "correct_answer": "to capture light energy",
            "options": [
                "To store glucose",
                "To capture light energy",
                "To produce ATP",
                "To break down carbon dioxide"
            ],
            "question_type": "multiple_choice",
            "concept_tag": "chlorophyll",
            "difficulty": "easy"
        },
        {
            "question_id": "q5",
            "question_text": "What is the final product of the Calvin Cycle?",
            "correct_answer": "glucose",
            "options": [
                "Oxygen",
                "ATP",
                "NADPH",
                "Glucose"
            ],
            "question_type": "multiple_choice",
            "concept_tag": "glucose",
            "difficulty": "medium"
        }
    ]
}


# ============================================================================
# MOCK DATA: User Answer Sets
# ============================================================================

# Scenario 1: All correct answers
USER_ANSWERS_ALL_CORRECT = {
    "q1": "to convert light energy into chemical energy stored in glucose",
    "q2": "thylakoid membranes",
    "q3": "false",
    "q4": "to capture light energy",
    "q5": "glucose"
}

# Scenario 2: Some incorrect answers (3/5 = 60%)
USER_ANSWERS_PARTIALLY_CORRECT = {
    "q1": "to convert light energy into chemical energy stored in glucose",  # Correct
    "q2": "stroma",  # Wrong
    "q3": "true",  # Wrong
    "q4": "to capture light energy",  # Correct
    "q5": "glucose"  # Correct
}

# Scenario 3: All incorrect answers
USER_ANSWERS_ALL_INCORRECT = {
    "q1": "to release carbon dioxide",  # Wrong
    "q2": "stroma",  # Wrong
    "q3": "true",  # Wrong
    "q4": "to produce atp",  # Wrong
    "q5": "oxygen"  # Wrong
}


# ============================================================================
# UNIT TESTS
# ============================================================================

def test_get_mastery_level():
    """Test the get_mastery_level helper function
    
    Thresholds:
    - >=80% → high
    - 50-79% → medium
    - <50% → low
    """
    print("\n" + "="*70)
    print("TEST: get_mastery_level()")
    print("="*70)

    test_cases = [
        (5, 5, "high"),      # 100%
        (4, 5, "high"),      # 80%
        (3, 5, "medium"),    # 60%
        (2, 5, "low"),       # 40% (< 50%)
        (1, 5, "low"),       # 20%
        (0, 5, "low"),       # 0%
    ]

    for score, total, expected in test_cases:
        result = get_mastery_level(score, total)
        percentage = (score / total * 100) if total > 0 else 0
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status}: {score}/{total} ({percentage:.0f}%) → {result} (expected: {expected})")


def test_generate_feedback():
    """Test the generate_feedback helper function"""
    print("\n" + "="*70)
    print("TEST: generate_feedback()")
    print("="*70)

    # Test high mastery with no weak concepts
    print("\n--- High Mastery (No weak concepts) ---")
    feedback = generate_feedback("high", [])
    print(feedback)
    assert "Excellent" in feedback or "moving on" in feedback
    print("✓ PASS: High mastery feedback generated")

    # Test medium mastery with weak concepts
    print("\n--- Medium Mastery (With weak concepts) ---")
    feedback = generate_feedback("medium", ["photosynthesis", "calvin_cycle"])
    print(feedback)
    assert "photosynthesis" in feedback and "calvin_cycle" in feedback
    print("✓ PASS: Medium mastery feedback with weak concepts generated")

    # Test low mastery with weak concepts
    print("\n--- Low Mastery (With weak concepts) ---")
    feedback = generate_feedback("low", ["light_reactions"])
    print(feedback)
    assert "light_reactions" in feedback
    print("✓ PASS: Low mastery feedback generated")


def test_assess_quiz_all_correct():
    """Test assess_quiz with all correct answers"""
    print("\n" + "="*70)
    print("TEST: assess_quiz() - All Correct Answers")
    print("="*70)

    result = assess_quiz(PHOTOSYNTHESIS_QUIZ, USER_ANSWERS_ALL_CORRECT)

    print(f"\nQuiz ID: {result['quiz_id']}")
    print(f"Score: {result['score']}/{result['total']}")
    print(f"Percentage: {result['percentage']:.1f}%")
    print(f"Mastery Level: {result['mastery_level']}")
    print(f"Weak Concepts: {result['weak_concepts']}")
    print(f"Strong Concepts: {result['strong_concepts']}")

    print(f"\n📝 Feedback:\n{result['feedback']}")

    print(f"\n📊 Summary: {result['summary']}")

    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")

    # Assertions
    assert result['score'] == 5, "Should have 5 correct answers"
    assert result['percentage'] == 100.0, "Should be 100%"
    assert result['mastery_level'] == "high", "Should be high mastery"
    assert len(result['weak_concepts']) == 0, "Should have no weak concepts"
    assert len(result['strong_concepts']) > 0, "Should have strong concepts"

    print("\n✓ PASS: All correct answers assessment")


def test_assess_quiz_partially_correct():
    """Test assess_quiz with partially correct answers"""
    print("\n" + "="*70)
    print("TEST: assess_quiz() - Partially Correct Answers")
    print("="*70)

    result = assess_quiz(PHOTOSYNTHESIS_QUIZ, USER_ANSWERS_PARTIALLY_CORRECT)

    print(f"\nQuiz ID: {result['quiz_id']}")
    print(f"Score: {result['score']}/{result['total']}")
    print(f"Percentage: {result['percentage']:.1f}%")
    print(f"Mastery Level: {result['mastery_level']}")
    print(f"Weak Concepts: {result['weak_concepts']}")
    print(f"Strong Concepts: {result['strong_concepts']}")

    print(f"\n📝 Feedback:\n{result['feedback']}")

    print(f"\n📊 Summary: {result['summary']}")

    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")

    print(f"\n📋 Question-by-Question Feedback:")
    for feedback in result['detailed_feedback']:
        status = "✓" if feedback['is_correct'] else "✗"
        print(f"  {status} {feedback['question_id']}: {feedback['feedback']}")

    # Assertions
    assert result['score'] == 3, "Should have 3 correct answers"
    assert result['percentage'] == 60.0, "Should be 60%"
    assert result['mastery_level'] == "medium", "Should be medium mastery"
    assert len(result['weak_concepts']) > 0, "Should have weak concepts"

    print("\n✓ PASS: Partially correct answers assessment")


def test_assess_quiz_all_incorrect():
    """Test assess_quiz with all incorrect answers"""
    print("\n" + "="*70)
    print("TEST: assess_quiz() - All Incorrect Answers")
    print("="*70)

    result = assess_quiz(PHOTOSYNTHESIS_QUIZ, USER_ANSWERS_ALL_INCORRECT)

    print(f"\nQuiz ID: {result['quiz_id']}")
    print(f"Score: {result['score']}/{result['total']}")
    print(f"Percentage: {result['percentage']:.1f}%")
    print(f"Mastery Level: {result['mastery_level']}")
    print(f"Weak Concepts: {result['weak_concepts']}")
    print(f"Strong Concepts: {result['strong_concepts']}")

    print(f"\n📝 Feedback:\n{result['feedback']}")

    print(f"\n📊 Summary: {result['summary']}")

    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")

    # Assertions
    assert result['score'] == 0, "Should have 0 correct answers"
    assert result['percentage'] == 0.0, "Should be 0%"
    assert result['mastery_level'] == "low", "Should be low mastery"
    assert len(result['weak_concepts']) > 0, "Should have weak concepts"
    assert len(result['strong_concepts']) == 0, "Should have no strong concepts"

    print("\n✓ PASS: All incorrect answers assessment")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ASSESSMENT AGENT - UNIT TESTS")
    print("="*70)

    try:
        # Run all tests
        test_get_mastery_level()
        test_generate_feedback()
        test_assess_quiz_all_correct()
        test_assess_quiz_partially_correct()
        test_assess_quiz_all_incorrect()

        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
