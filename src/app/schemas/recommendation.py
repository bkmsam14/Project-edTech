"""
Pydantic schemas for Recommendation tooling.

Consumed by RecommendationTool and RecommendationEngine.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class NextStepResult(BaseModel):
    """
    The recommended next learning action for a learner on a topic.

    Produced by RecommendationEngine.get_next_step().
    """

    action: str                         # "remediate" | "review" | "advance"
    topic: str
    reason: str
    suggested_difficulty: Optional[str] = None   # beginner | developing | proficient | advanced
    suggested_content_type: Optional[str] = None # e.g. "visual", "audio", "text"


class DifficultyResult(BaseModel):
    """
    The recommended difficulty level for a learner on a topic.

    Produced by RecommendationEngine.get_next_difficulty().
    """

    topic: str
    recommended_difficulty: str         # beginner | developing | proficient | advanced
    reason: str
    current_avg_score: Optional[float] = None


class RevisionItem(BaseModel):
    """One item in a revision plan."""

    topic: str
    action: str                         # "remediate" | "review"
    priority: str                       # "high" | "medium"
    reason: str


class RevisionPlan(BaseModel):
    """
    A prioritised list of topics to revise.

    Produced by RecommendationEngine.get_revision_plan().
    """

    user_id: str
    tenant_id: str
    items: list[RevisionItem]
    total_topics: int
