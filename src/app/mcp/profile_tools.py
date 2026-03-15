"""
Profile MCP tools — thin wrappers exposing ProfileService to agents.

Architecture rule:
    Agents must NOT call ProfileService or Supabase user tables directly.
    These functions are the ONLY public interface for profile operations.

Module-level singleton _service is wired to supabase_admin at import time.
Override _service in tests:  profile_tools._service = ProfileService(mock_client)
"""

from __future__ import annotations

from typing import Optional

from src.app.schemas.profile import ProfileCreate, ProfileOut, ProfilePatch
from src.app.services.profile_service import ProfileService
from src.database.client import supabase_admin

_service = ProfileService(supabase_admin)


def profile_get(user_id: str) -> Optional[dict]:
    """
    Fetch a learner profile.

    Called by any agent that needs to know the learner's support mode,
    accessibility settings, or learning level.

    Args:
        user_id: Learner identifier.

    Returns:
        Serialised ProfileOut dict, or None if not found.
    """
    result: Optional[ProfileOut] = _service.get_profile(user_id)
    return result.model_dump() if result else None


def profile_create(
    tenant_id: str,
    user_id: str,
    full_name: str,
    email: str,
    learning_level: str = "beginner",
    grade_level: Optional[str] = None,
    language: str = "en",
    support_mode: str = "standard",
) -> dict:
    """
    Create a new learner profile.

    Called by the onboarding flow when a new user registers.

    Returns:
        Serialised ProfileOut dict.
    """
    data = ProfileCreate(
        tenant_id=tenant_id,
        user_id=user_id,
        full_name=full_name,
        email=email,
        learning_level=learning_level,
        grade_level=grade_level,
        language=language,
        support_mode=support_mode,
    )
    return _service.create_profile(data).model_dump()


def profile_update(
    user_id: str,
    full_name: Optional[str] = None,
    learning_level: Optional[str] = None,
    grade_level: Optional[str] = None,
    language: Optional[str] = None,
    support_mode: Optional[str] = None,
) -> dict:
    """
    Partially update a learner profile.

    Only non-None arguments are written. Called by the Accessibility Agent
    or UI when the learner changes preferences.

    Returns:
        Updated ProfileOut dict.
    """
    patch = ProfilePatch(
        full_name=full_name,
        learning_level=learning_level,
        grade_level=grade_level,
        language=language,
        support_mode=support_mode,
    )
    return _service.update_profile(user_id, patch).model_dump()


def profile_update_learning_state(
    user_id: str,
    topic: str,
    mastery: float,
    weak: bool,
    risk_level: Optional[str] = None,
) -> bool:
    """
    Update the learner's coarse-grained learning level from observed mastery.

    Called by the Assessment Agent after scoring a quiz.
    Detailed per-topic analytics are written separately via analytics_tools.

    Args:
        user_id:    Learner identifier.
        topic:      Topic that was assessed.
        mastery:    Numeric mastery score (0.0 – 1.0).
        weak:       True if avg score < remediation threshold.
        risk_level: Optional risk label ("high"|"medium"|"low").

    Returns:
        True if the update succeeded.
    """
    return _service.update_learning_state(user_id, topic, mastery, weak, risk_level)
