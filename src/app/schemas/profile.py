"""
Pydantic schemas for Profile tooling.

Agents read these schemas when calling ProfileTool.
ProfileService converts LearnerProfile dataclasses to these models so
the rest of the system has a single, typed, JSON-serialisable contract.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ProfileCreate(BaseModel):
    """Minimum data required to create a new learner profile."""

    tenant_id: str
    user_id: str
    full_name: str
    email: str
    learning_level: str = "beginner"    # beginner | developing | proficient | advanced
    grade_level: Optional[str] = None
    language: str = "en"
    support_mode: str = "standard"      # standard | dyslexia | adhd | dyscalculia | ...


class ProfilePatch(BaseModel):
    """Fields that can be updated on an existing profile (all optional)."""

    full_name: Optional[str] = None
    learning_level: Optional[str] = None
    grade_level: Optional[str] = None
    language: Optional[str] = None
    support_mode: Optional[str] = None


class AccessibilityOut(BaseModel):
    """Flattened accessibility settings relevant to agents."""

    use_tts: bool = False
    tts_speed: float = 1.0
    tts_voice: Optional[str] = None
    font_size: Optional[str] = None
    use_dyslexic_font: bool = False
    high_contrast: bool = False
    simplified_language: bool = False


class ProfileOut(BaseModel):
    """
    Canonical learner profile view returned by ProfileTool.

    Agents consume this — not the raw LearnerProfile dataclass.
    """

    user_id: str
    tenant_id: Optional[str] = None
    full_name: str
    email: Optional[str] = None
    learning_level: str
    grade_level: Optional[str] = None
    language: str = "en"
    support_mode: str
    use_tts: bool = False
    accessibility: AccessibilityOut = AccessibilityOut()
    mastery_levels: dict = {}           # topic_id -> "beginner"|"developing"|etc.
    preferences: dict = {}
