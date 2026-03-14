"""
Example usage of the Orchestrator Agent

This demonstrates how to:
1. Initialize the orchestrator
2. Register step handlers (mock implementations)
3. Process requests
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.orchestrator import Orchestrator
from orchestrator.schemas import (
    OrchestratorRequest,
    WorkflowStep,
    WorkflowContext
)


# Mock step handlers (these would be replaced with actual agent implementations)

def mock_load_profile(context: WorkflowContext) -> dict:
    """Mock handler for loading user profile"""
    print(f"  > Loading profile for user: {context.request.user_id}")

    # Simulate profile data
    profile = {
        'user_id': context.request.user_id,
        'support_mode': 'dyslexia',
        'preferences': {
            'font_size': 'large',
            'line_spacing': 'wide',
            'use_tts': True
        },
        'learning_level': 'intermediate',
        'mastery_levels': {
            'math_basics': 0.85,
            'algebra': 0.60
        }
    }

    # Update context
    context.user_profile = profile

    return profile


def mock_retrieve_lesson(context: WorkflowContext) -> dict:
    """Mock handler for retrieving lesson content"""
    print(f"  > Retrieving lesson: {context.request.lesson_id}")

    # Simulate retrieved chunks
    chunks = [
        {
            'chunk_id': 'chunk_1',
            'content': 'Algebra is a branch of mathematics that uses symbols...',
            'relevance_score': 0.95
        },
        {
            'chunk_id': 'chunk_2',
            'content': 'Variables are symbols that represent unknown values...',
            'relevance_score': 0.87
        }
    ]

    # Update context
    context.retrieved_chunks = chunks
    context.lesson_content = {
        'lesson_id': context.request.lesson_id,
        'title': 'Introduction to Algebra',
        'chunks': chunks
    }

    return {'chunks': chunks, 'count': len(chunks)}


def mock_adapt_accessibility(context: WorkflowContext) -> dict:
    """Mock handler for accessibility adaptation"""
    print(f"  > Adapting for support mode: {context.user_profile.get('support_mode')}")

    # Simulate dyslexia-friendly adaptations
    adaptations = {
        'font': 'OpenDyslexic',
        'font_size': 18,
        'line_spacing': 2.0,
        'text_chunking': 'short_sentences',
        'color_scheme': 'cream_background',
        'simplified_language': True
    }

    # Update context
    context.accessibility_adaptations = adaptations

    return adaptations


def mock_tutor_explanation(context: WorkflowContext) -> dict:
    """Mock handler for tutor explanation"""
    print(f"  > Generating explanation for: {context.request.message[:50]}...")

    # Simulate explanation
    explanation = {
        'content': """
Algebra is a way to solve problems using letters and symbols.

Think of it like a puzzle. Instead of knowing all the numbers,
some are hidden. We use letters like 'x' or 'y' to represent
these hidden numbers.

For example: x + 5 = 10
Here, x is the mystery number. What number plus 5 equals 10?
The answer is 5!
        """.strip(),
        'difficulty_level': 'beginner',
        'grounded_in_lesson': True
    }

    return explanation


def mock_generate_quiz(context: WorkflowContext) -> dict:
    """Mock handler for quiz generation"""
    print(f"  > Generating quiz from lesson content")

    quiz = {
        'quiz_id': f"quiz_{datetime.utcnow().timestamp()}",
        'questions': [
            {
                'id': 'q1',
                'question': 'What does a variable represent in algebra?',
                'type': 'multiple_choice',
                'options': [
                    'A known number',
                    'An unknown value',
                    'A mathematical operation',
                    'A formula'
                ],
                'correct_answer': 'An unknown value'
            },
            {
                'id': 'q2',
                'question': 'If x + 3 = 7, what is x?',
                'type': 'short_answer',
                'correct_answer': '4'
            }
        ],
        'lesson_id': context.request.lesson_id
    }

    return quiz


def mock_assess_quiz(context: WorkflowContext) -> dict:
    """Mock handler for quiz assessment"""
    print(f"  > Assessing quiz answers")

    assessment = {
        'score': 0.75,
        'correct_answers': 3,
        'total_questions': 4,
        'feedback': [
            {
                'question_id': 'q1',
                'correct': True,
                'feedback': 'Great job!'
            },
            {
                'question_id': 'q2',
                'correct': False,
                'feedback': 'Not quite. Remember x + 3 = 7 means x = 7 - 3'
            }
        ],
        'weak_topics': ['basic_equations']
    }

    return assessment


def mock_recommend(context: WorkflowContext) -> dict:
    """Mock handler for recommendations"""
    print(f"  > Generating personalized recommendations")

    recommendations = {
        'next_lessons': [
            {
                'lesson_id': 'algebra_102',
                'title': 'Solving Simple Equations',
                'difficulty': 'beginner',
                'reason': 'Build on your current understanding'
            }
        ],
        'practice_exercises': [
            {
                'exercise_id': 'ex_001',
                'title': 'Variable Practice',
                'estimated_time': '10 minutes'
            }
        ],
        'revision_topics': ['basic_equations']
    }

    return recommendations


def mock_validate_guardrails(context: WorkflowContext) -> dict:
    """Mock handler for guardrails validation"""
    print(f"  > Validating output guardrails")

    validation = {
        'grounded_in_lesson': True,
        'no_diagnosis_claims': True,
        'appropriate_language': True,
        'within_scope': True,
        'confidence_score': 0.92,
        'passed': True
    }

    return validation


def mock_retrieve_history(context: WorkflowContext) -> dict:
    """Mock handler for retrieving user history"""
    print(f"  > Retrieving learning history")

    history = {
        'recent_lessons': ['algebra_101', 'math_basics_05'],
        'quiz_scores': [0.8, 0.75, 0.9],
        'time_spent': '2.5 hours',
        'last_session': '2026-03-13'
    }

    return history


async def main():
    """Main example function"""
    print("=" * 60)
    print("ORCHESTRATOR AGENT - EXAMPLE USAGE")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = Orchestrator()

    # Register mock step handlers
    print("\n1. Registering step handlers...")
    orchestrator.register_step_handler(WorkflowStep.LOAD_PROFILE, mock_load_profile)
    orchestrator.register_step_handler(WorkflowStep.RETRIEVE_LESSON, mock_retrieve_lesson)
    orchestrator.register_step_handler(WorkflowStep.ADAPT_ACCESSIBILITY, mock_adapt_accessibility)
    orchestrator.register_step_handler(WorkflowStep.TUTOR_EXPLANATION, mock_tutor_explanation)
    orchestrator.register_step_handler(WorkflowStep.GENERATE_QUIZ, mock_generate_quiz)
    orchestrator.register_step_handler(WorkflowStep.ASSESS_QUIZ, mock_assess_quiz)
    orchestrator.register_step_handler(WorkflowStep.RECOMMEND, mock_recommend)
    orchestrator.register_step_handler(WorkflowStep.VALIDATE_GUARDRAILS, mock_validate_guardrails)
    orchestrator.register_step_handler(WorkflowStep.RETRIEVE_HISTORY, mock_retrieve_history)
    print("   [OK] All handlers registered")

    # Example 1: Explain lesson request
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Explain Lesson Request")
    print("=" * 60)

    request1 = OrchestratorRequest(
        user_id="student_123",
        message="Can you explain what algebra is?",
        lesson_id="algebra_101",
        session_id="session_001"
    )

    print(f"\nUser message: '{request1.message}'")
    print("\nWorkflow execution:")

    response1 = await orchestrator.process_request(request1)

    print(f"\n[OK] Response:")
    print(f"  Success: {response1.success}")
    print(f"  Intent: {response1.intent.value}")
    print(f"  Message: {response1.message}")
    print(f"  Steps executed: {', '.join(response1.workflow_steps_executed)}")

    # Example 2: Generate quiz request
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Generate Quiz Request")
    print("=" * 60)

    request2 = OrchestratorRequest(
        user_id="student_123",
        message="Give me a quiz to test my understanding",
        lesson_id="algebra_101",
        session_id="session_001"
    )

    print(f"\nUser message: '{request2.message}'")
    print("\nWorkflow execution:")

    response2 = await orchestrator.process_request(request2)

    print(f"\n[OK] Response:")
    print(f"  Success: {response2.success}")
    print(f"  Intent: {response2.intent.value}")
    print(f"  Message: {response2.message}")
    if response2.data and 'quiz' in response2.data:
        print(f"  Quiz questions: {len(response2.data['quiz'].get('questions', []))}")
    else:
        print(f"  Quiz questions: N/A (workflow failed)")

    # Example 3: Recommendation request
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Recommendation Request")
    print("=" * 60)

    request3 = OrchestratorRequest(
        user_id="student_123",
        message="What should I learn next?",
        session_id="session_001"
    )

    print(f"\nUser message: '{request3.message}'")
    print("\nWorkflow execution:")

    response3 = await orchestrator.process_request(request3)

    print(f"\n[OK] Response:")
    print(f"  Success: {response3.success}")
    print(f"  Intent: {response3.intent.value}")
    print(f"  Message: {response3.message}")
    if response3.data and 'recommendations' in response3.data:
        print(f"  Recommended lessons: {len(response3.data['recommendations'].get('next_lessons', []))}")
    else:
        print(f"  Recommended lessons: N/A (workflow failed)")

    # Example 4: Workflow info (debugging)
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Workflow Info (Debugging)")
    print("=" * 60)

    test_messages = [
        "Explain photosynthesis",
        "Make this simpler",
        "Test me on this topic",
        "What should I study next?"
    ]

    for msg in test_messages:
        info = orchestrator.get_workflow_info(msg)
        print(f"\n'{msg}'")
        print(f"  > Intent: {info['intent']} (confidence: {info['confidence']:.2f})")
        print(f"  > Steps: {' -> '.join(info['workflow_steps'])}")

    print("\n" + "=" * 60)
    print("EXAMPLES COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
