"""Profile handler - LOAD_PROFILE workflow step"""
import logging
from database import SessionLocal
from models.user_model import User

logger = logging.getLogger(__name__)


async def load_profile_handler(context):
    """
    Load user profile from database.

    Input (from context):
        - context.request.user_id: User identifier

    Output:
        - user_profile: Dict with user data and settings
        - stores in context.user_profile
    """
    try:
        user_id = context.request.user_id

        # Query user from database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()

            if not user:
                logger.warning(f"User {user_id} not found, creating mock profile")
                # Return default profile if user doesn't exist
                return {
                    "user_id": user_id,
                    "name": "Student",
                    "support_mode": "dyslexia",
                    "learning_level": "intermediate",
                    "accessibility_settings": {
                        "font_family": "sans-serif",
                        "font_size": "16px",
                        "line_height": "1.8",
                        "letter_spacing": "0.1em"
                    },
                    "mastery_levels": {}
                }

            user_profile = {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "support_mode": user.support_mode,
                "learning_level": user.learning_level,
                "accessibility_settings": user.accessibility_settings,
                "mastery_levels": user.mastery_levels,
                "preferences": user.preferences
            }

            logger.info(f"Loaded profile for user {user_id}")
            return user_profile

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        raise
