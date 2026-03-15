"""Retrieval handler - RETRIEVE_LESSON and RETRIEVE_HISTORY workflow steps

Fixes applied:
  1. CRITICAL: Now sets context.retrieved_chunks and context.lesson_content directly
     (previously returned dict but never populated context attributes)
  2. Tries vector store search first, falls back to SQLAlchemy
  3. Adds DEBUG_RAG observability at every step
"""
import logging
import os
import sys

logger = logging.getLogger(__name__)

DEBUG_RAG = os.environ.get("DEBUG_RAG", "").lower() in ("1", "true", "yes")


def _debug(msg: str, **kwargs):
    """Print debug info when DEBUG_RAG is enabled."""
    if DEBUG_RAG:
        extra = " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        print(f"[DEBUG_RAG][retrieval] {msg}  {extra}")
    logger.info(msg)


# ---------------------------------------------------------------------------
# Vector store search (preferred path)
# ---------------------------------------------------------------------------

def _try_vector_search(query_text: str, tenant_id: str = "default"):
    """
    Attempt semantic search via the app/mcp retrieval layer (ChromaDB).

    Returns (chunks_list, success_bool).
    Each chunk is a dict with keys: chunk_id, document_id, content, score, ...
    """
    try:
        # Add project root so src.app imports resolve
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from src.app.mcp.retrieval_tools import retrieval_search_chunks

        _debug("Vector store search starting", query=query_text[:80], tenant=tenant_id)
        results = retrieval_search_chunks(
            query_text=query_text,
            tenant_id=tenant_id,
            top_k=5,
            score_threshold=0.15,
        )
        _debug("Vector store returned results", count=len(results))

        if DEBUG_RAG and results:
            for i, r in enumerate(results[:3]):
                print(f"  [DEBUG_RAG]  chunk #{i}: score={r.get('score', '?'):.3f} "
                      f"doc={r.get('document_id', '?')} "
                      f"preview={r.get('content', '')[:100]}...")

        if results:
            # Convert SearchResult dicts to the chunk format handlers expect
            chunks = [
                {
                    "text": r["content"],
                    "chunk_id": r.get("chunk_id", ""),
                    "document_id": r.get("document_id", ""),
                    "score": r.get("score", 0),
                    "relevance": r.get("score", 1.0),
                    "source": "vector_store",
                }
                for r in results
            ]
            return chunks, True

        _debug("Vector store returned 0 results — falling through to SQLAlchemy")
        return [], False

    except Exception as e:
        _debug(f"Vector store unavailable: {e}")
        return [], False


# ---------------------------------------------------------------------------
# SQLAlchemy fallback (legacy path)
# ---------------------------------------------------------------------------

def _try_sqlalchemy_search(lesson_id: str):
    """
    Fallback: load lesson from SQLAlchemy/SQLite and generate sentence chunks.

    Returns (lesson_dict_or_None, chunks_list).
    """
    try:
        from database import SessionLocal
        from models.lesson_model import Lesson

        _debug("SQLAlchemy fallback lookup", lesson_id=lesson_id)

        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()

            if not lesson:
                _debug(f"Lesson {lesson_id} not in SQLAlchemy DB")
                return None, []

            lesson.generate_chunks()
            chunks = lesson.get_chunks()

            lesson_content = {
                "lesson_id": lesson.lesson_id,
                "title": lesson.title,
                "description": lesson.description,
                "subject": lesson.subject,
                "content": lesson.content,
                "difficulty": lesson.difficulty,
                "estimated_time_minutes": lesson.estimated_time_minutes,
                "tags": lesson.tags,
                "prerequisites": lesson.prerequisites,
            }

            _debug("SQLAlchemy returned lesson", title=lesson.title, chunk_count=len(chunks))
            return lesson_content, chunks
        finally:
            db.close()

    except Exception as e:
        _debug(f"SQLAlchemy fallback failed: {e}")
        return None, []


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

async def retrieve_lesson_handler(context):
    """
    Retrieve lesson content and populate context for downstream handlers.

    CRITICAL: This handler MUST set:
      - context.retrieved_chunks   (list of chunk dicts)
      - context.lesson_content     (dict with lesson metadata + content)
    """
    lesson_id = context.request.lesson_id
    user_query = context.request.message

    _debug("=== RETRIEVE_LESSON START ===",
           lesson_id=str(lesson_id), query=user_query[:80])

    # --- Strategy 1: Vector store (semantic search) ---
    search_query = user_query or ""
    tenant_id = context.request.context.get("tenant_id", "default") if context.request.context else "default"

    vs_chunks, vs_ok = _try_vector_search(search_query, tenant_id)

    if vs_ok and vs_chunks:
        # Build lesson_content from the top-scoring chunk's document metadata
        context.retrieved_chunks = vs_chunks
        context.lesson_content = {
            "lesson_id": lesson_id or vs_chunks[0].get("document_id", ""),
            "title": "Retrieved Content",
            "content": "\n\n".join(c["text"] for c in vs_chunks),
            "source": "vector_store",
        }
        _debug("Context populated from VECTOR STORE",
               chunk_count=len(vs_chunks),
               content_len=len(context.lesson_content["content"]))
        return {
            "lesson_content": context.lesson_content,
            "retrieved_chunks": context.retrieved_chunks,
            "source": "vector_store",
        }

    # --- Strategy 2: SQLAlchemy fallback ---
    if lesson_id:
        lesson_content, sq_chunks = _try_sqlalchemy_search(lesson_id)
        if lesson_content and sq_chunks:
            context.lesson_content = lesson_content
            context.retrieved_chunks = sq_chunks
            _debug("Context populated from SQLALCHEMY",
                   chunk_count=len(sq_chunks),
                   content_len=len(lesson_content.get("content", "")))
            return {
                "lesson_content": context.lesson_content,
                "retrieved_chunks": context.retrieved_chunks,
                "source": "sqlalchemy",
            }

    # --- Nothing found ---
    _debug("WARNING: No content found from any source")
    context.retrieved_chunks = []
    context.lesson_content = None
    return {"error": "No lesson content found", "source": "none"}


# ---------------------------------------------------------------------------
# History handler (unchanged, included for completeness)
# ---------------------------------------------------------------------------

async def retrieve_history_handler(context):
    """Retrieve user's learning history from database."""
    try:
        user_id = context.user_profile.get("user_id") if context.user_profile else None
        if not user_id:
            logger.warning("No user_id in context")
            return {"history": []}

        from database import SessionLocal
        from models.history_model import LearningHistory

        db = SessionLocal()
        try:
            history_records = db.query(LearningHistory)\
                .filter(LearningHistory.user_id == user_id)\
                .order_by(LearningHistory.created_at.desc())\
                .all()
            history = [record.to_dict() for record in history_records]
            logger.info(f"Retrieved {len(history)} history records for user {user_id}")
            return {"history": history}
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise
