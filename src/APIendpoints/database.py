"""Database initialization and session management

NOTE: Database is currently disabled pending Supabase configuration.
When Supabase is set up, add these environment variables:
  - SUPABASE_URL: Your Supabase project URL
  - SUPABASE_ANON_KEY: Your Supabase anon key
  - SUPABASE_SERVICE_KEY: Your Supabase service role key

Then set DATABASE_ENABLED = True in config.py
"""
import logging
import os
from dotenv import load_dotenv
from config import DATABASE_URL, DATABASE_ENABLED
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

logger = logging.getLogger(__name__)

# Base class for ORM models
Base = declarative_base()

# Database will be initialized when configured
engine = None
SessionLocal = None

# Supabase clients
_supabase_client = None
_supabase_admin = None


def get_supabase_client():
    """
    Get Supabase client with anon key (respects RLS policies)
    Use this for user-facing operations
    """
    global _supabase_client

    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")

    if _supabase_client is None:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    return _supabase_client


def get_supabase_admin():
    """
    Get Supabase admin client with service key (bypasses RLS)
    Use this for backend operations that need full access
    """
    global _supabase_admin

    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")

    if _supabase_admin is None:
        from supabase import create_client
        _supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    return _supabase_admin


def init_db():
    """Initialize database tables (only if enabled)"""
    if not DATABASE_ENABLED:
        logger.warning("⚠️  Database is DISABLED - pending Supabase configuration")
        logger.info("To enable database, set SUPABASE_* environment variables and set DATABASE_ENABLED=True in config.py")
        return

    try:
        global engine, SessionLocal
        engine = create_engine(DATABASE_URL, echo=False, future=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
        Base.metadata.create_all(bind=engine)
        logger.info(f"✅ Database initialized with URL: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def get_db():
    """Get database session"""
    if not SessionLocal:
        logger.warning("Database not initialized")
        return None

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database():
    """Seed database with sample data (only if enabled)"""
    if not DATABASE_ENABLED:
        logger.info("⏭️  Database seeding skipped (database disabled)")
        return

    if not SessionLocal:
        logger.warning("Cannot seed database - SessionLocal not initialized")
        return

    try:
        from models.user_model import User
        from models.lesson_model import Lesson

        db = SessionLocal()
        try:
            # Check if data already exists
            existing_user = db.query(User).filter(User.user_id == "student_1").first()
            if existing_user:
                logger.info("Database already seeded with sample data")
                return

            # Create sample users
            users = [
                User(
                    user_id="student_1",
                    name="Alice Johnson",
                    email="alice@example.com",
                    support_mode="dyslexia",
                    learning_level="intermediate"
                ),
                User(
                    user_id="student_2",
                    name="Bob Smith",
                    email="bob@example.com",
                    support_mode="dyslexia",
                    learning_level="beginner"
                ),
                User(
                    user_id="student_3",
                    name="Carol White",
                    email="carol@example.com",
                    support_mode="dyslexia",
                    learning_level="advanced"
                )
            ]

            for user in users:
                db.add(user)

            db.commit()
            logger.info(f"Created {len(users)} sample users")

            # Create sample lessons
            lessons = [
                Lesson(
                    lesson_id="bio_101",
                    title="Introduction to Biology",
                    description="Basics of biology and life sciences",
                    content="Biology is the scientific study of life...",
                    subject="Biology",
                    difficulty="beginner"
                ),
                Lesson(
                    lesson_id="bio_photosynthesis",
                    title="Photosynthesis",
                    description="How plants convert light energy to chemical energy",
                    content="Photosynthesis is the process by which plants, algae, and some bacteria convert light energy...",
                    subject="Biology",
                    difficulty="intermediate"
                ),
                Lesson(
                    lesson_id="algebra_101",
                    title="Introduction to Algebra",
                    description="Fundamentals of algebraic expressions and equations",
                    content="Algebra is a branch of mathematics that deals with symbols...",
                    subject="Mathematics",
                    difficulty="beginner"
                ),
            ]

            for lesson in lessons:
                db.add(lesson)

            db.commit()
            logger.info(f"Created {len(lessons)} sample lessons")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
