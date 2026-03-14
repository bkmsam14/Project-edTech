"""Lesson database model"""
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Lesson(Base):
    """Lesson content model"""
    __tablename__ = "lessons"

    lesson_id = Column(String(100), primary_key=True, index=True)
    title = Column(String(300))
    description = Column(String(1000))
    subject = Column(String(100), index=True)  # Biology, Math, History, etc

    # Main content
    content = Column(Text)  # Full lesson text

    # Content chunks for retrieval
    chunks = Column(JSON, default=[])  # List of content chunks with metadata

    # Metadata
    difficulty = Column(String(50))  # beginner, intermediate, advanced
    estimated_time_minutes = Column(Integer, default=30)

    # Tags for categorization
    tags = Column(JSON, default=[])

    # Prerequisites
    prerequisites = Column(JSON, default=[])  # List of lesson_ids that should be completed first

    # Quiz questions associated with this lesson
    quiz_questions = Column(JSON, default=[])

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    learning_history = relationship("LearningHistory", back_populates="lesson")

    def get_chunks(self):
        """Get content chunks for RAG"""
        if not self.chunks:
            # Auto-generate chunks from content if not set
            self.generate_chunks()
        return self.chunks

    def generate_chunks(self):
        """Generate content chunks by splitting on sentences/paragraphs"""
        if not self.content:
            return

        # Simple chunking: split by periods and group into chunks
        sentences = self.content.split('.')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            current_chunk += sentence + ". "

            # Create chunk if it reaches ~200 characters
            if len(current_chunk) > 200:
                chunks.append({
                    "text": current_chunk.strip(),
                    "order": len(chunks),
                    "relevance": 1.0
                })
                current_chunk = ""

        # Add remaining text as final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "order": len(chunks),
                "relevance": 1.0
            })

        self.chunks = chunks

    def to_dict(self):
        return {
            "lesson_id": self.lesson_id,
            "title": self.title,
            "description": self.description,
            "subject": self.subject,
            "content": self.content,
            "difficulty": self.difficulty,
            "estimated_time_minutes": self.estimated_time_minutes,
            "tags": self.tags,
            "prerequisites": self.prerequisites
        }

    def __repr__(self):
        return f"<Lesson {self.lesson_id}>"
