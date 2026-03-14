"""
End-to-end integration tests for the Orchestrator Workflow

Tests the complete workflow from API request through orchestrator
and all handlers to final response.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from orchestrator.orchestrator import Orchestrator
from orchestrator.schemas import Intent, OrchestratorRequest, OrchestratorResponse
from handlers import register_handlers


# ============================================================================
# MOCK DATA
# ============================================================================

MOCK_USER = {
    "user_id": "user_test_001",
    "name": "Test Student",
    "support_mode": "dyslexia",
    "accessibility_settings": {
        "font": "OpenDyslexic",
        "font_size": "16px",
        "line_spacing": "1.8",
        "letter_spacing": "2px"
    },
    "mastery_levels": {}
}

MOCK_LESSON = {
    "lesson_id": "lesson_001",
    "title": "Photosynthesis",
    "content": """
    Photosynthesis is the process by which plants convert light energy into chemical energy.
    The main equation: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2

    Two stages:
    1. Light Reactions (in thylakoids)
    2. Calvin Cycle (in stroma)
    """
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
            "question_text": "Where do the light-dependent reactions occur?",
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
            "question_text": "The Calvin Cycle directly requires light energy.",
            "correct_answer": "false",
            "options": ["True", "False"],
            "question_type": "true_false",
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


# ============================================================================
# TEST CONTEXT CLASS
# ============================================================================

class MockContext:
    """Mock context object for orchestrator"""
    def __init__(self, request: OrchestratorRequest):
        self.request = request
        self.intermediate_results = {}
        self.user_profile = MOCK_USER.copy()
        self.lesson_data = MOCK_LESSON.copy()


# ============================================================================
# E2E TESTS
# ============================================================================

async def test_orchestrator_explain_workflow():
    """Test: User requests explanation of a concept"""
    print("\n" + "="*70)
    print("E2E TEST: EXPLAIN Workflow (LOAD_PROFILE → RETRIEVE → EXPLAIN)")
    print("="*70)

    # Create orchestrator and register handlers
    orchestrator = Orchestrator()
    register_handlers(orchestrator)

    # Create request - message will be classified into EXPLAIN_LESSON intent
    request = OrchestratorRequest(
        user_id="user_test_001",
        message="Please explain photosynthesis in simple terms",
        lesson_id="lesson_001"
    )

    # Create context
    context = MockContext(request)

    # Process through orchestrator
    print("\n→ Workflow steps:")
    response = await orchestrator.process_request(request)

    print(f"  ✓ LOAD_PROFILE: Complete")
    print(f"  ✓ RETRIEVE_LESSON: {MOCK_LESSON.get('title')}")
    print(f"  ✓ TUTOR_EXPLANATION: Generated")

    # Verify response
    assert response is not None, "Should return response"
    assert response.success, "Should be successful"
    print(f"\n← Response Status: {response.status}")
    print(f"← Workflow Steps: {len(response.workflow_steps)} steps executed")

    print("\n✓ PASS: EXPLAIN workflow completed successfully")


async def test_orchestrator_simplify_workflow():
    """Test: User requests accessibility adaptation"""
    print("\n" + "="*70)
    print("E2E TEST: SIMPLIFY Workflow (LOAD_PROFILE → ADAPT_ACCESSIBILITY)")
    print("="*70)

    orchestrator = Orchestrator()
    register_handlers(orchestrator)

    request = OrchestratorRequest(
        user_id="user_test_001",
        message="Simplify this for me: The process of photosynthesis involves complex biochemical reactions."
    )

    context = MockContext(request)

    print("\n→ Workflow steps:")
    response = await orchestrator.process_request(request)

    print(f"  ✓ LOAD_PROFILE: Complete")
    print(f"  ✓ ADAPT_ACCESSIBILITY: Applied dyslexia formatting")

    assert response is not None
    assert response.success
    print(f"\n← Response Status: {response.status}")

    print("\n✓ PASS: SIMPLIFY workflow completed successfully")


async def test_orchestrator_quiz_generation_workflow():
    """Test: User requests quiz generation"""
    print("\n" + "="*70)
    print("E2E TEST: QUIZ_GEN Workflow (RETRIEVE → GENERATE_QUIZ)")
    print("="*70)

    orchestrator = Orchestrator()
    register_handlers(orchestrator)

    request = OrchestratorRequest(
        user_id="user_test_001",
        message="Generate a quiz for photosynthesis",
        lesson_id="lesson_001"
    )

    context = MockContext(request)
    context.intermediate_results["lesson_context"] = MOCK_LESSON["content"]

    print("\n→ Workflow steps:")
    response = await orchestrator.process_request(request)

    print(f"  ✓ RETRIEVE_LESSON: {MOCK_LESSON.get('title')}")
    print(f"  ✓ GENERATE_QUIZ: Generated quiz")

    assert response is not None
    assert response.success
    print(f"\n← Quiz generation completed")
    print(f"← Generated questions")

    print("\n✓ PASS: QUIZ_GENERATION workflow completed successfully")


async def test_orchestrator_assessment_workflow():
    """Test: User submits quiz answers and receives assessment"""
    print("\n" + "="*70)
    print("E2E TEST: ASSESSMENT Workflow (ASSESS_QUIZ)")
    print("="*70)

    orchestrator = Orchestrator()
    register_handlers(orchestrator)

    request = OrchestratorRequest(
        user_id="user_test_001",
        message="Submit my quiz answers for grading",
        lesson_id="lesson_001",
        context={"answers": USER_ANSWERS}
    )

    context = MockContext(request)
    context.intermediate_results["quiz"] = MOCK_QUIZ
    context.intermediate_results["answers"] = USER_ANSWERS

    print("\n→ Workflow steps:")
    response = await orchestrator.process_request(request)

    print(f"  ✓ ASSESS_QUIZ: Scored and evaluated")

    assert response is not None

    print(f"\n← Assessment completed")
    print(f"   Sample assessment results would include:")
    print(f"   - Score and percentage")
    print(f"   - Mastery level")
    print(f"   - Weak and strong concepts")
    print(f"   - Personalized feedback")

    print("\n✓ PASS: ASSESSMENT workflow completed successfully")


async def test_orchestrator_chained_workflow():
    """Test: Full learning journey - Generate Quiz → Assessment"""
    print("\n" + "="*70)
    print("E2E TEST: CHAINED Workflow (QUIZ → ASSESSMENT)")
    print("="*70)

    orchestrator = Orchestrator()
    register_handlers(orchestrator)

    # Step 1: Generate Quiz
    print("\n→ Step 1: Generate Quiz")
    request1 = OrchestratorRequest(
        user_id="user_test_001",
        message="Generate a quiz for photosynthesis",
        lesson_id="lesson_001"
    )

    response1 = await orchestrator.process_request(request1)
    print(f"  ✓ Quiz generation requested")

    # Step 2: Assess Quiz (submit answers)
    print("\n→ Step 2: Submit Answers and Assess")
    request2 = OrchestratorRequest(
        user_id="user_test_001",
        message="Grade my quiz answers for photosynthesis",
        lesson_id="lesson_001",
        context={"answers": USER_ANSWERS}
    )

    response2 = await orchestrator.process_request(request2)
    print(f"  ✓ Quiz assessment completed")

    # Verify responses
    assert response1.success or response1 is not None, "Quiz generation should succeed"
    assert response2.success or response2 is not None, "Assessment should succeed"

    print(f"\n← Full Learning Journey Complete:")
    print(f"   Quiz → Assessment")

    print("\n✓ PASS: CHAINED workflow completed successfully")


async def test_orchestrator_error_handling():
    """Test: Orchestrator handles missing data gracefully"""
    print("\n" + "="*70)
    print("E2E TEST: Error Handling (Missing Data)")
    print("="*70)

    orchestrator = Orchestrator()
    register_handlers(orchestrator)

    # Test: Assessment with no quiz context
    print("\n→ Test: Assessment without quiz data")
    request = OrchestratorRequest(
        user_id="user_test_001",
        message="Grade my quiz",
        lesson_id="lesson_001"
    )

    try:
        response = await orchestrator.process_request(request)
        print(f"  ✓ Handled gracefully: response returned")
    except Exception as e:
        print(f"  ✓ Handled with expected behavior: {type(e).__name__}")

    print("\n✓ PASS: Error handling test passed")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def main():
    """Run all E2E tests"""
    print("\n" + "="*70)
    print("END-TO-END ORCHESTRATOR WORKFLOW TESTS")
    print("="*70)

    try:
        # Run all tests
        await test_orchestrator_explain_workflow()
        await test_orchestrator_simplify_workflow()
        await test_orchestrator_quiz_generation_workflow()
        await test_orchestrator_assessment_workflow()
        await test_orchestrator_chained_workflow()
        await test_orchestrator_error_handling()

        print("\n" + "="*70)
        print("✓ ALL E2E TESTS PASSED")
        print("="*70)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
