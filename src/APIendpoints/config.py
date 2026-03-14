"""Configuration settings for EduAI Backend"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR}/eduai.db"
DATABASE_PATH = BASE_DIR / "eduai.db"

# Supabase configuration (fill in when ready)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")  # https://xxxx.supabase.co
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # API key
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")  # DB password

# Use Supabase if credentials available, otherwise fallback to SQLite
if SUPABASE_URL and SUPABASE_DB_PASSWORD:
    DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{SUPABASE_URL.split('//')[1]}:5432/postgres"

# Database is disabled until configured
DATABASE_ENABLED = False  # Set to True once Supabase credentials are added

# Application
APP_NAME = "EduAI - Educational Platform"
APP_VERSION = "1.0.0"
DEBUG = True

# Accessibility defaults
DEFAULT_SUPPORT_MODE = "dyslexia"
ACCESSIBILITY_SETTINGS = {
    "dyslexia": {
        "font_family": "sans-serif",
        "font_size": "16px",
        "line_height": "1.8",
        "letter_spacing": "0.1em",
        "word_spacing": "0.2em",
        "background_color": "#f5f5f0",
        "text_color": "#000000"
    }
}

# API Settings
API_PREFIX = "/api/v1"
CORS_ORIGINS = ["*"]

# Learning settings
QUIZ_DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
RECOMMENDATION_DEPTH_LIMIT = 5
DEFAULT_NUM_QUIZ_QUESTIONS = 5

# Mastery thresholds
MASTERY_THRESHOLD = {
    "beginner": 0.0,
    "developing": 0.4,
    "proficient": 0.7,
    "advanced": 0.9
}

# Handler configuration
HANDLERS_CONFIG = {
    "timeout_seconds": 30,
    "retry_count": 3
}
