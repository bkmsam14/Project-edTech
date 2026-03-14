"""User database model"""
from sqlalchemy import Column, String, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """User profile model"""
    __tablename__ = "users"

    user_id = Column(String(100), primary_key=True, index=True)
    name = Column(String(200))
    email = Column(String(200), unique=True, index=True)
    support_mode = Column(String(50), default="dyslexia")  # dyslexia, visual_impairment, etc
    learning_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced

    # Accessibility settings
    accessibility_settings = Column(JSON, default={
        "font_family": "sans-serif",
        "font_size": "16px",
        "line_height": "1.8",
        "letter_spacing": "0.1em"
    })

    # Mastery levels for topics {topic: score}
    mastery_levels = Column(JSON, default={})

    # Preferences
    preferences = Column(JSON, default={
        "notifications_enabled": True,
        "difficulty_preference": "medium"
    })

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    learning_history = relationship("LearningHistory", back_populates="user")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "support_mode": self.support_mode,
            "learning_level": self.learning_level,
            "accessibility_settings": self.accessibility_settings,
            "mastery_levels": self.mastery_levels,
            "preferences": self.preferences
        }

    def __repr__(self):
        return f"<User {self.user_id}>"
