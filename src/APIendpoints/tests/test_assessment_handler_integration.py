"""
Simple sanity test for assessment handler integration
Tests the assessment handler directly without full orchestrator
"""

import sys
import os
import asyncio

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from handlers.assessment_handler import assess_quiz_handler


class MockRequest:
    def __init__(self, user_id, lesson_id="lesson_001", answers=None):
        self.user_id = user_id
        self.lesson_id = lesson_id
        self.answers = answers or {}


class MockContext:
    def __init__(self, request, quiz_data, user_answers):
        self.request = request
        self.user_profile = {
            "user_id": request.user_id,
            "name": "Test User",
            "support_mode": "dyslexia"
        }
        self.intermediate_results = {
            "quiz": quiz_data,
            "answers": user_answers
        }


MOCK_QUIZ = {
    "quiz_id": "quiz_001",
    "topic": "Photosynthesis",
    "difficulty": "intermediate",
    "questions": [
        {
            "question_id": "q1",
            "question_text": "What is the main function of photosynthesis?",
            "correct_answer": "to convert light energy into chemical energy stored in glucose",
            "concept_tag": "photosynthesis",
            "difficulty": "easy"
        },
        {
            "question_id": "q2",
            "question_text": "Where do the light-dependent reactions occur?",
            "correct_answer": "thylakoid membranes",
            "concept_tag": "light_reactions",
            "difficulty": "medium"
        },
        {
            "question_id": "q3",
            "question_text": "The Calvin Cycle directly requires light energy.",
            "correct_answer": "false",
            "concept_tag": "calvin_cycle",
            "difficulty": "medium"
        }
    ]
}

USER_ANSWERS = {
    "q1": "to convert light energy into chemical energy stored in glucose",  # Correct
    "q2": "stroma",  # Wrong
    "q3": "false"  # Correct
}


async def test_assessment_handler_integration():
    """Test the assessment handler with mock context"""
    print("\n" + "="*70)
    print("ASSESSMENT HANDLER INTEGRATION TEST")
    print("="*70)

    # Create mock request and context
    request = MockRequest("user_test_001", "lesson_001", USER_ANSWERS)
    context = MockContext(request, MOCK_QUIZ, USER_ANSWERS)

    # Call the assessment handler
    print("\n→ Calling assess_quiz_handler...")
    result = await assess_quiz_handler(context)

    # Verify results
    print(f"\n← Assessment Results:")
    print(f"   Score: {result.get('score')}/{result.get('total')}")
    print(f"   Percentage: {result.get('percentage'):.1f}%")
    print(f"   Mastery Level: {result.get('mastery_level')}")
    print(f"   Weak Concepts: {result.get('weak_concepts')}")
    print(f"   Strong Concepts: {result.get('strong_concepts')}")
    print(f"   Feedback: {result.get('feedback')[:100]}...")
    print(f"   Passed: {result.get('passed')}")

    # Assertions
    assert result['score'] == 2, f"Expected 2 correct, got {result['score']}"
    assert result['total'] == 3, f"Expected total 3, got {result['total']}"
    assert result['percentage'] == 66.7, f"Expected 66.7%, got {result['percentage']}"
    assert result['mastery_level'] == "medium", f"Expected medium mastery, got {result['mastery_level']}"
    assert len(result['weak_concepts']) == 1, "Should have 1 weak concept"
    assert "light_reactions" in result['weak_concepts'], "light_reactions should be weak"
    assert len(result['strong_concepts']) == 2, "Should have 2 strong concepts"
    assert result['feedback'], "Should have feedback"
    assert result['passed'] == False, "Should not have passed (66.7% < high mastery)"

    print("\n✓ PASS: Assessment handler integration test successful")


if __name__ == "__main__":
    try:
        asyncio.run(test_assessment_handler_integration())
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
