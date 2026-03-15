"""Profile handler - LOAD_PROFILE workflow step"""
import logging
from config import DATABASE_ENABLED
from database import SessionLocal
from models.user_model import User

logger = logging.getLogger(__name__)


def _default_profile(user_id: str) -> dict:
    """Return a default mock learner profile."""
    return {
        "user_id": user_id,
        "name": "Student",
        "support_mode": "dyslexia",
        "preferred_format": "visual",
        "academic_level": "intermediate",
        "learning_level": "intermediate",
        "accessibility_settings": {
            "font_family": "sans-serif",
            "font_size": "16px",
            "line_height": "1.8",
            "letter_spacing": "0.1em"
        },
        "mastery_levels": {}
    }


async def load_profile_handler(context):
    """
    Load user profile from database.
    Falls back to a default mock profile when the database is disabled
    or when the user is not found.

    Input (from context):
        - context.request.user_id: User identifier

    Output:
        - user_profile: Dict with user data and settings
        - stores in context.user_profile
    """
    user_id = context.request.user_id

    # Fallback when database is disabled
    if not DATABASE_ENABLED:
        logger.info(f"Database disabled — returning fallback mock profile for user {user_id}")
        return _default_profile(user_id)

    try:
        db = SessionLocal()
        if db is None:
            logger.warning(f"SessionLocal returned None — returning fallback mock profile for user {user_id}")
            return _default_profile(user_id)

        try:
            user = db.query(User).filter(User.user_id == user_id).first()

            if not user:
                logger.warning(f"User {user_id} not found in DB — returning fallback mock profile")
                return _default_profile(user_id)

            user_profile = {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "support_mode": user.support_mode,
                "preferred_format": user.preferences.get("format", "visual") if user.preferences else "visual",
                "academic_level": user.learning_level,
                "learning_level": user.learning_level,
                "accessibility_settings": user.accessibility_settings,
                "mastery_levels": user.mastery_levels,
                "preferences": user.preferences
            }

            logger.info(f"Loaded profile for user {user_id} from database")
            return user_profile

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error loading profile: {e} — returning fallback mock profile for user {user_id}")
        return _default_profile(user_id)
