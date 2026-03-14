"""Learning history model"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class LearningHistory(Base):
    """Track user learning progress"""
    __tablename__ = "learning_history"

    history_id = Column(String(100), primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), index=True)
    lesson_id = Column(String(100), ForeignKey("lessons.lesson_id"), index=True)

    # Activity type
    activity_type = Column(String(50))  # lesson_view, quiz_attempt, assessment, practice

    # Performance metrics
    score = Column(Float, nullable=True)  # 0.0 to 1.0
    time_spent_seconds = Column(Integer, default=0)
    completion_status = Column(String(50))  # started, in_progress, completed

    # Quiz/Assessment specific data
    answers = Column(JSON, default={})  # Submitted answers
    feedback = Column(JSON, default={})  # Grading feedback

    # Metadata
    notes = Column(String(1000), nullable=True)
    session_id = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="learning_history")
    lesson = relationship("Lesson", back_populates="learning_history")

    def to_dict(self):
        return {
            "history_id": self.history_id,
            "user_id": self.user_id,
            "lesson_id": self.lesson_id,
            "activity_type": self.activity_type,
            "score": self.score,
            "time_spent_seconds": self.time_spent_seconds,
            "completion_status": self.completion_status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<LearningHistory {self.history_id}>"
