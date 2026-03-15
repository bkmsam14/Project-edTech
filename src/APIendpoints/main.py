from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directories to path
sys.path.insert(0, os.path.dirname(__file__))  # Add APIendpoints to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))  # Add src to path

# Import simplified orchestrator
try:
    from orchestrator.orchestrator_simple import Orchestrator
    logger.info("✓ Imported simplified Orchestrator")
except ImportError:
    # Fallback to complex orchestrator
    from orchestrator.orchestrator import Orchestrator
    logger.info("✓ Imported full-featured Orchestrator (fallback)")

from database import init_db, seed_database

# Initialize database (disabled until Supabase is configured)
logger.info("Initializing database...")
try:
    init_db()
    seed_database()
    logger.info("✓ Database initialized and seeded")
except Exception as e:
    logger.warning(f"⚠️  Database initialization failed (this is OK if Supabase not configured yet): {e}")
    logger.info("Backend will work without database until Supabase credentials are provided")
    logger.info("📝 To enable Supabase: Set SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_PASSWORD environment variables")

# Initialize FastAPI app
app = FastAPI(
    title="EduAI - Educational Platform API",
    description="API for AI-powered educational platform with dyslexia support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PART 7: Initialize global orchestrator instance
logger.info("🚀 Initializing Orchestrator...")
orchestrator = Orchestrator()

# Register all workflow handlers with the orchestrator
from handlers import register_handlers
register_handlers(orchestrator)

logger.info("✓ Orchestrator ready for use")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "service": "EduAI API",
        "version": "1.0.0",
        "orchestrator": "initialized"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "EduAI Educational Platform API",
        "version": "1.0.0",
        "description": "AI-powered learning platform with dyslexia support",
        "endpoints": {
            "health": "/health",
            "quiz": "/api/v1/quiz/generate",
            "assessment": "/api/v1/assessment/submit",
            "explain": "/api/v1/explain",
            "simplify": "/api/v1/simplify",
            "recommendations": "/api/v1/recommendations",
            "qa": "/api/v1/qa"
        }
    }


# Import routes
from routes import explain, simplify, quiz, assessment, recommendations, qa

# Include routers
app.include_router(explain.router, prefix="/api/v1", tags=["Learning"])
app.include_router(simplify.router, prefix="/api/v1", tags=["Accessibility"])
app.include_router(quiz.router, prefix="/api/v1", tags=["Quiz"])
app.include_router(assessment.router, prefix="/api/v1", tags=["Assessment"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(qa.router, prefix="/api/v1", tags=["Q&A"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
