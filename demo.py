#!/usr/bin/env python3
"""
Demo script for EdTech Agents - Hackathon showcase
Run this to see both agents in action
"""

import sys
import io

# Fix Windows console encoding issues
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from edtech_agents import (
    assessment_agent,
    get_student_topic_summary,
    reset_student_topic_history,
    tutor_agent,
)


def print_separator():
    print("\n" + "=" * 80 + "\n")


def demo_tutor_agent():
    print("🎓 TUTOR AGENT DEMO")
    print_separator()

    lesson_chunks = [
        "Recursion is when a function calls itself to solve a problem. "
        "Every recursive function needs a base case to stop the recursion.",
        "The base case is the simplest version of the problem that can be solved directly. "
        "Without a base case, the function would call itself forever.",
        "Recursive functions break down complex problems into smaller, similar problems. "
        "Each recursive call solves a smaller piece until reaching the base case.",
    ]

    print("📚 Lesson Chunks:")
    for i, chunk in enumerate(lesson_chunks, 1):
        print(f"  {i}. {chunk[:80]}...")
    print()

    question = "What stops a recursive function from running forever?"
    print(f"❓ Student Question: {question}")
    print()

    # Demo with increasing hint levels
    for hints_used in [0, 1, 2]:
        print(f"\n--- Hints Used: {hints_used} ---")
        result = tutor_agent(
            student_id="demo-student",
            question=question,
            lesson_chunks=lesson_chunks,
            dyslexia_mode=True,
            hints_used=hints_used,
        )

        print(f"\n💡 Hints ({len(result['hints'])} available):")
        for hint in result["hints"]:
            print(f"  Level {hint['level']} [{hint['support_level']}]: {hint['text']}")

        if hints_used == 0:
            print(f"\n📝 Quiz Questions ({len(result['quiz'])} generated):")
            for i, q in enumerate(result["quiz"], 1):
                print(f"\n  Question {i} ({q['type']}):")
                print(f"    {q['question']}")
                if q['type'] == 'multiple_choice':
                    print(f"    Options: {', '.join(q['options'])}")
                print(f"    ✓ Correct: {q['correct_answer']}")


def demo_assessment_agent():
    print_separator()
    print("📊 ASSESSMENT AGENT DEMO")
    print_separator()

    reset_student_topic_history()

    scenarios = [
        {
            "name": "Scenario 1: Correct answer, no hints",
            "student_answer": "base case",
            "correct_answer": "base case",
            "hints_used": 0,
        },
        {
            "name": "Scenario 2: Correct answer, needed hints",
            "student_answer": "the base case stops it",
            "correct_answer": "base case",
            "hints_used": 2,
        },
        {
            "name": "Scenario 3: Wrong answer, many hints",
            "student_answer": "a loop variable",
            "correct_answer": "base case",
            "hints_used": 3,
        },
    ]

    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"  Student: '{scenario['student_answer']}'")
        print(f"  Correct: '{scenario['correct_answer']}'")
        print(f"  Hints Used: {scenario['hints_used']}")

        result = assessment_agent(
            student_id="demo-student",
            question_id=f"q-{scenarios.index(scenario) + 1}",
            student_answer=scenario["student_answer"],
            correct_answer=scenario["correct_answer"],
            hints_used=scenario["hints_used"],
            topic="recursion",
        )

        print(f"\n  ✓ Correct: {result['is_correct']}")
        print(f"  📉 Weakness Score: {result['weakness_score']}")
        print(f"  👉 Next Action: {result['recommendation']['next_action']}")
        print(f"  💬 Message: {result['recommendation']['message']}")

    print_separator()
    print("📈 STUDENT TOPIC SUMMARY")
    print_separator()

    summary = get_student_topic_summary("demo-student")
    for topic, stats in summary.items():
        print(f"\nTopic: {topic}")
        print(f"  Attempts: {stats['attempts']}")
        print(f"  Incorrect: {stats['incorrect']}")
        print(f"  Hints Used: {stats['hints_used']}")
        print(f"  Mastery Score: {stats['mastery_score']:.2f}")


def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "EDTECH AGENTS - HACKATHON DEMO")
    print("=" * 80)

    demo_tutor_agent()
    demo_assessment_agent()

    print("\n" + "=" * 80)
    print(" " * 30 + "🎉 DEMO COMPLETE!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
