"""
Personalization handler - Assembles user learning context for AI model
"""

import logging
from typing import Dict, List, Any
from database import get_supabase_admin

logger = logging.getLogger(__name__)


async def get_learning_context(user_id: str) -> Dict[str, Any]:
    """
    Assemble comprehensive learning context from quiz history and mastery data
    This context is used by the AI model for personalization

    Args:
        user_id: User ID

    Returns:
        Dict with learning context for AI model
    """
    try:
        supabase_admin = get_supabase_admin()

        # Get recent quiz performance (last 10 quizzes)
        recent_quizzes = supabase_admin.table("quiz_attempts")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        # Get mastery levels
        mastery = supabase_admin.table("mastery_levels")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

        # Get struggling topics
        struggling_topics = supabase_admin.table("mastery_levels")\
            .select("subject, topic, mastery_score")\
            .eq("user_id", user_id)\
            .eq("is_struggling", True)\
            .execute()

        # Get mastered topics
        mastered_topics = supabase_admin.table("mastery_levels")\
            .select("subject, topic, mastery_score")\
            .eq("user_id", user_id)\
            .eq("is_mastered", True)\
            .execute()

        # Get risk flags (if any)
        risks = supabase_admin.table("risk_flags")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("is_resolved", False)\
            .execute()

        # Calculate performance metrics
        quiz_data = recent_quizzes.data if recent_quizzes.data else []
        avg_score = 0
        total_quizzes = len(quiz_data)

        if quiz_data:
            avg_score = sum(q.get("score_pct", 0) for q in quiz_data) / len(quiz_data)

        # Collect all weak topics from recent quizzes
        all_weak_topics = []
        for quiz in quiz_data:
            all_weak_topics.extend(quiz.get("weak_topics", []))

        # Count topic frequency
        weak_topic_counts = {}
        for topic in all_weak_topics:
            weak_topic_counts[topic] = weak_topic_counts.get(topic, 0) + 1

        # Sort by frequency
        most_common_weak_topics = sorted(
            weak_topic_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5 weak topics

        # Determine difficulty adjustment recommendation
        difficulty_adjustment = "maintain"
        if avg_score > 85:
            difficulty_adjustment = "increase"
        elif avg_score < 60:
            difficulty_adjustment = "decrease"

        # Build learning context for AI
        context = {
            "user_id": user_id,
            "performance_summary": {
                "recent_quiz_count": total_quizzes,
                "average_score": round(avg_score, 2),
                "passing_rate": round(
                    sum(1 for q in quiz_data if q.get("passed", False)) / total_quizzes * 100, 2
                ) if total_quizzes > 0 else 0,
                "total_questions_attempted": sum(q.get("total_questions", 0) for q in quiz_data)
            },
            "mastery_profile": {
                topic.get("topic"): round(topic.get("mastery_score", 0), 2)
                for topic in (mastery.data if mastery.data else [])
            },
            "struggling_areas": [
                {
                    "subject": t.get("subject"),
                    "topic": t.get("topic"),
                    "mastery_score": round(t.get("mastery_score", 0), 2)
                }
                for t in (struggling_topics.data if struggling_topics.data else [])
            ],
            "mastered_areas": [
                {
                    "subject": t.get("subject"),
                    "topic": t.get("topic"),
                    "mastery_score": round(t.get("mastery_score", 0), 2)
                }
                for t in (mastered_topics.data if mastered_topics.data else [])
            ],
            "frequent_weak_topics": [
                {"topic": topic, "count": count}
                for topic, count in most_common_weak_topics
            ],
            "risk_level": risks.data[0].get("risk_level") if risks.data else "low",
            "personalization_hints": {
                "difficulty_adjustment": difficulty_adjustment,
                "focus_topics": [t["topic"] for t in (struggling_topics.data if struggling_topics.data else [])],
                "avoid_topics": [t["topic"] for t in (mastered_topics.data if mastered_topics.data else [])],
                "recommended_quiz_type": "revision" if avg_score < 70 else "practice"
            }
        }

        logger.info(f"Assembled learning context for user {user_id}: avg_score={avg_score:.2f}%, {len(struggling_topics.data if struggling_topics.data else [])} struggling topics")

        return context

    except Exception as e:
        logger.error(f"Error getting learning context: {str(e)}")
        # Return minimal context on error
        return {
            "user_id": user_id,
            "performance_summary": {
                "recent_quiz_count": 0,
                "average_score": 0,
                "passing_rate": 0,
                "total_questions_attempted": 0
            },
            "personalization_hints": {
                "difficulty_adjustment": "maintain",
                "focus_topics": [],
                "recommended_quiz_type": "practice"
            }
        }


async def get_personalized_quiz_config(user_id: str) -> Dict[str, Any]:
    """
    Get personalized quiz configuration based on learning context

    Returns recommended quiz parameters
    """
    context = await get_learning_context(user_id)

    hints = context.get("personalization_hints", {})
    struggling = context.get("struggling_areas", [])
    avg_score = context.get("performance_summary", {}).get("average_score", 0)

    # Determine difficulty
    difficulty = "medium"
    if hints.get("difficulty_adjustment") == "increase":
        difficulty = "hard"
    elif hints.get("difficulty_adjustment") == "decrease":
        difficulty = "easy"

    # Determine number of questions based on performance
    num_questions = 5  # default
    if avg_score > 80:
        num_questions = 7  # More questions for high performers
    elif avg_score < 50:
        num_questions = 3  # Fewer questions for struggling students

    # Topics to focus on
    focus_topics = [area.get("topic") for area in struggling[:3]]  # Top 3 struggling areas

    return {
        "difficulty": difficulty,
        "num_questions": num_questions,
        "quiz_type": hints.get("recommended_quiz_type", "practice"),
        "focus_topics": focus_topics,
        "reasoning": {
            "average_score": avg_score,
            "difficulty_rationale": f"Adjusted to {difficulty} based on {avg_score:.1f}% average score",
            "topic_rationale": f"Focusing on {len(focus_topics)} struggling areas" if focus_topics else "General practice"
        }
    }


async def format_learning_context_for_prompt(user_id: str) -> str:
    """
    Format learning context as a string prompt for AI model

    Returns formatted string to inject into AI prompts
    """
    context = await get_learning_context(user_id)

    perf = context.get("performance_summary", {})
    struggling = context.get("struggling_areas", [])
    mastered = context.get("mastered_areas", [])
    hints = context.get("personalization_hints", {})

    prompt = f"""
Student Learning Profile:
- Recent Performance: {perf.get('average_score', 0):.1f}% average score ({perf.get('recent_quiz_count', 0)} quizzes)
- Passing Rate: {perf.get('passing_rate', 0):.1f}%
"""

    if struggling:
        prompt += "\nStruggling Areas:\n"
        for area in struggling[:5]:  # Top 5
            prompt += f"  - {area['topic']} (mastery: {area['mastery_score']*100:.0f}%)\n"

    if mastered:
        prompt += "\nMastered Topics:\n"
        for area in mastered[:3]:  # Top 3
            prompt += f"  - {area['topic']} (mastery: {area['mastery_score']*100:.0f}%)\n"

    prompt += f"\nRecommended Approach: {hints.get('recommended_quiz_type', 'practice').title()}"
    prompt += f"\nDifficulty Recommendation: {hints.get('difficulty_adjustment', 'maintain').title()}"

    if hints.get('focus_topics'):
        prompt += f"\nTopics to Focus On: {', '.join(hints['focus_topics'][:3])}"

    return prompt.strip()
