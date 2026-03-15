"""
ProfileService — canonical read/write interface for learner profiles.

Architecture rule:
    Agents must NOT access Supabase user tables directly.
    All profile reads and writes go through ProfileService (or ProfileTool).

Read path:  delegates to LearnerProfileModule (existing, already-tested logic).
Write path: uses supabase_admin directly for create / update operations.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.app.schemas.profile import AccessibilityOut, ProfileCreate, ProfileOut, ProfilePatch

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Lazy imports — LearnerProfileModule may not be importable in all
# test environments (requires Supabase env vars at import time in
# some configurations).
# ------------------------------------------------------------------
try:
    from src.learner_profile.learner_profile import LearnerProfileModule
    _module_available = True
except Exception:  # pragma: no cover
    _module_available = False


def _mastery_label(score: float) -> str:
    """Convert a numeric mastery score (0-1) to a categorical label."""
    if score >= 0.9:
        return "advanced"
    if score >= 0.7:
        return "proficient"
    if score >= 0.4:
        return "developing"
    return "beginner"


class ProfileService:
    """
    Shared profile service for all agents.

    Constructor accepts an admin Supabase client (bypasses RLS) and an
    optional LearnerProfileModule for the read path.

    Usage:
        from src.database.client import supabase_admin
        service = ProfileService(supabase_admin)
    """

    def __init__(self, client: Any, profile_module: Any = None) -> None:
        self._db = client
        if profile_module is not None:
            self._module = profile_module
        elif _module_available:
            self._module = LearnerProfileModule()
        else:
            self._module = None

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_profile(self, user_id: str) -> Optional[ProfileOut]:
        """
        Fetch a learner profile and return it as a ProfileOut.

        Delegates read logic to LearnerProfileModule (reads all 4 Supabase
        tables: users, support_settings, accessibility_settings,
        learning_preferences).

        Args:
            user_id: Learner identifier.

        Returns:
            ProfileOut or None if learner not found.
        """
        if self._module is None:
            logger.error("LearnerProfileModule unavailable — cannot read profile")
            return None

        profile = self._module.get_profile(user_id)
        if profile is None:
            return None

        return self._to_profile_out(profile)

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def create_profile(self, data: ProfileCreate) -> ProfileOut:
        """
        Create a new learner profile (users + support_settings rows).

        Args:
            data: ProfileCreate — required learner fields.

        Returns:
            ProfileOut with the created data.
        """
        # --- users row ---
        user_row = {
            "user_id": data.user_id,
            "full_name": data.full_name,
            "email": data.email,
            "learning_level": data.learning_level,
            "grade_level": data.grade_level,
            "language": data.language,
        }
        self._db.table("users").insert(user_row).execute()

        # --- support_settings row ---
        support_row = {
            "user_id": data.user_id,
            "support_mode": data.support_mode,
            "support_active": True,
        }
        self._db.table("support_settings").insert(support_row).execute()

        logger.info("profile created user_id=%s", data.user_id)

        return ProfileOut(
            user_id=data.user_id,
            tenant_id=data.tenant_id,
            full_name=data.full_name,
            email=data.email,
            learning_level=data.learning_level,
            grade_level=data.grade_level,
            language=data.language,
            support_mode=data.support_mode,
        )

    def update_profile(self, user_id: str, patch: ProfilePatch) -> ProfileOut:
        """
        Partially update a learner profile.

        Updates the users table (and support_settings if support_mode changed).

        Args:
            user_id: Learner identifier.
            patch:   ProfilePatch — only non-None fields are written.

        Returns:
            Updated ProfileOut (re-read after write).
        """
        # Build users-table update payload (ignore None values)
        user_payload = patch.model_dump(
            exclude_none=True,
            exclude={"support_mode"},
        )
        if user_payload:
            self._db.table("users").update(user_payload).eq("user_id", user_id).execute()

        # Update support_settings separately if provided
        if patch.support_mode is not None:
            self._db.table("support_settings").update(
                {"support_mode": patch.support_mode}
            ).eq("user_id", user_id).execute()

        logger.info("profile updated user_id=%s fields=%s", user_id, list(user_payload.keys()))

        # Re-read and return fresh profile
        updated = self.get_profile(user_id)
        if updated is None:
            # Fallback: return minimal ProfileOut from the patch data
            return ProfileOut(
                user_id=user_id,
                full_name=patch.full_name or "",
                learning_level=patch.learning_level or "beginner",
                support_mode=patch.support_mode or "standard",
            )
        return updated

    def update_learning_state(
        self,
        user_id: str,
        topic: str,
        mastery: float,
        weak: bool,
        risk_level: Optional[str] = None,
    ) -> bool:
        """
        Update the learner's overall learning_level on their profile based
        on observed mastery.

        Called by the Assessment Agent after scoring a quiz.  The detailed
        per-topic mastery lives in the analytics learner_topic_state table;
        this method updates the coarse profile-level learning_level only.

        Args:
            user_id:    Learner identifier.
            topic:      Topic ID (logged but not stored in the profile table).
            mastery:    Numeric mastery score (0.0 – 1.0).
            weak:       True if the learner is struggling (triggers level-down guard).
            risk_level: Optional risk label ("high"|"medium"|"low").

        Returns:
            True if the update succeeded.
        """
        new_level = _mastery_label(mastery)

        # Guard: never automatically downgrade if learner is struggling — let
        # the Assessment Agent decide on explicit remediation instead.
        if weak and new_level == "advanced":
            new_level = "proficient"

        try:
            self._db.table("users").update(
                {"learning_level": new_level}
            ).eq("user_id", user_id).execute()
            logger.info(
                "learning_state updated user=%s topic=%s mastery=%.2f level=%s",
                user_id, topic, mastery, new_level,
            )
            return True
        except Exception as exc:
            logger.error("update_learning_state failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_profile_out(self, profile: Any) -> ProfileOut:
        """Convert a LearnerProfile dataclass to ProfileOut."""
        d = profile.to_dict() if hasattr(profile, "to_dict") else vars(profile)

        accessibility = AccessibilityOut(
            use_tts=bool(d.get("use_tts", False)),
            tts_speed=float(d.get("tts_speed", 1.0)),
            tts_voice=d.get("tts_voice"),
            font_size=d.get("font_size"),
            use_dyslexic_font=bool(d.get("use_dyslexic_font", False)),
            high_contrast=bool(d.get("high_contrast", False)),
            simplified_language=bool(d.get("simplified_language", False)),
        )

        return ProfileOut(
            user_id=str(d.get("user_id", "")),
            full_name=str(d.get("full_name", "")),
            email=d.get("email"),
            learning_level=str(d.get("learning_level", "beginner")),
            grade_level=d.get("grade_level"),
            language=str(d.get("language", "en")),
            support_mode=str(d.get("support_mode", "standard")),
            use_tts=bool(d.get("use_tts", False)),
            accessibility=accessibility,
            preferences={
                "learning_style": d.get("learning_style"),
                "preferred_formats": d.get("preferred_formats", []),
                "pacing": d.get("pacing", "normal"),
                "quiz_time_limit": d.get("quiz_time_limit"),
            },
        )
