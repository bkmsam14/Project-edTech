"""Tutor handler - TUTOR_EXPLANATION workflow step

Fixes applied:
  1. CRITICAL: Now calls the LLM (via ai_utils) with retrieved context
     (previously was pure string concatenation with zero AI)
  2. Falls back to string concatenation if Ollama is unreachable
  3. Adds DEBUG_RAG observability showing prompt assembly and LLM usage
"""
import logging
import os

logger = logging.getLogger(__name__)

DEBUG_RAG = os.environ.get("DEBUG_RAG", "").lower() in ("1", "true", "yes")


def _debug(msg: str, **kwargs):
    """Print debug info when DEBUG_RAG is enabled."""
    if DEBUG_RAG:
        extra = " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        print(f"[DEBUG_RAG][tutor] {msg}  {extra}")
    logger.info(msg)


async def tutor_explanation_handler(context):
    """
    Generate educational explanation from lesson content.

    Pipeline:
      1. Assemble context from retrieved_chunks
      2. Call LLM with context-grounded prompt (ai_utils)
      3. Fall back to string concatenation if LLM unavailable

    Input (from context):
        - context.request.message: User's question/request
        - context.retrieved_chunks: Content chunks (set by retrieval_handler)
        - context.lesson_content: Lesson metadata (set by retrieval_handler)
        - context.user_profile: User profile (for personalization)

    Output:
        - explanation: Generated explanation text
        - sources: Source chunk metadata
        - confidence: Confidence score
        - generation_method: "llm" | "rule_based"
    """
    try:
        user_question = context.request.message
        chunks = context.retrieved_chunks or []
        lesson = context.lesson_content or {}

        _debug("=== TUTOR_EXPLANATION START ===",
               question=user_question[:80],
               chunk_count=len(chunks),
               has_lesson=bool(lesson))

        if not chunks:
            _debug("WARNING: No chunks available for explanation")
            return {
                "explanation": "I don't have enough content to explain this topic. "
                               "Please make sure course content has been ingested.",
                "sources": [],
                "confidence": 0.0,
                "generation_method": "none",
            }

        # --- Assemble context from chunks ---
        chunk_texts = [c.get("text", c.get("content", "")) for c in chunks[:5]]
        assembled_context = "\n\n".join(chunk_texts)

        _debug("Assembled context for LLM",
               context_chars=len(assembled_context),
               num_chunks_used=len(chunk_texts))

        if DEBUG_RAG:
            print(f"  [DEBUG_RAG]  Context preview (first 500 chars):\n"
                  f"  {assembled_context[:500]}...")

        # --- Strategy 1: LLM-powered explanation ---
        explanation = None
        generation_method = "rule_based"

        try:
            from utils.ai_utils import (
                is_ollama_available,
                call_local_model_with_context,
                build_explanation_prompt,
                call_local_model,
            )

            if is_ollama_available() and len(assembled_context) > 20:
                _debug("Strategy 1: LLM explanation via Ollama")

                # Build a well-structured prompt grounded in the retrieved context
                dyslexia_mode = False
                if context.user_profile:
                    support_mode = context.user_profile.get("support_mode", "standard")
                    dyslexia_mode = support_mode in ("dyslexia", "adhd", "dyscalculia")

                prompt = build_explanation_prompt(
                    lesson_context=assembled_context,
                    user_question=user_question,
                    for_dyslexic_learners=dyslexia_mode,
                )

                if DEBUG_RAG:
                    print(f"  [DEBUG_RAG]  Final prompt length: {len(prompt)} chars")
                    print(f"  [DEBUG_RAG]  Prompt preview:\n  {prompt[:400]}...")

                explanation = call_local_model(prompt, temperature=0.5)

                if explanation:
                    generation_method = "llm"
                    _debug("LLM explanation generated",
                           response_chars=len(explanation))
                else:
                    _debug("LLM returned empty — falling through to rule-based")

        except ImportError:
            _debug("ai_utils not importable — using rule-based fallback")
        except Exception as e:
            _debug(f"LLM call failed: {e} — using rule-based fallback")

        # --- Strategy 2: Rule-based fallback ---
        if not explanation:
            _debug("Strategy 2: Rule-based string concatenation")
            title = lesson.get("title", "this topic")
            explanation_parts = [
                f"Let me explain {title}. Based on your question about "
                f"'{user_question[:50]}...', here's what you need to know:",
            ]
            for chunk in chunks[:3]:
                explanation_parts.append(chunk.get("text", chunk.get("content", "")))
            explanation_parts.append(
                "Does this help clarify the concept? Feel free to ask "
                "if you need more details or examples."
            )
            explanation = " ".join(explanation_parts)
            generation_method = "rule_based"

        # --- Build source metadata ---
        sources = []
        for i, chunk in enumerate(chunks[:5]):
            sources.append({
                "chunk_index": i,
                "chunk_id": chunk.get("chunk_id", str(i)),
                "document_id": chunk.get("document_id", ""),
                "score": chunk.get("score", chunk.get("relevance", 1.0)),
                "preview": chunk.get("text", chunk.get("content", ""))[:100],
                "source": chunk.get("source", "unknown"),
            })

        confidence = 0.9 if generation_method == "llm" else 0.6

        _debug("=== TUTOR_EXPLANATION DONE ===",
               method=generation_method,
               explanation_chars=len(explanation),
               source_count=len(sources))

        return {
            "explanation": explanation,
            "sources": sources,
            "confidence": confidence,
            "generation_method": generation_method,
        }

    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise
