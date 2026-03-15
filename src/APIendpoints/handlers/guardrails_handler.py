"""Guardrails handler — VALIDATE_GUARDRAILS workflow step.

Delegates to GuardrailsEngine (src/Guardrails/guardrails_engine.py) which uses
qwen2.5:3b via Ollama for LLM-powered checks. Falls back to rule-based checks
if the engine is unavailable.
"""
import logging
import sys
import os

logger = logging.getLogger(__name__)

# Make src/ importable regardless of the working directory
_src_path = os.path.join(os.path.dirname(__file__), "..", "..", "..")
if _src_path not in sys.path:
    sys.path.insert(0, os.path.abspath(_src_path))

try:
    from Guardrails.guardrails_engine import GuardrailsEngine
    _engine = GuardrailsEngine()
    _ENGINE_AVAILABLE = True
    logger.info("GuardrailsEngine loaded (qwen2.5:3b)")
except Exception as _e:
    _ENGINE_AVAILABLE = False
    logger.warning("GuardrailsEngine not available (%s) — using rule-based fallback", _e)


async def validate_guardrails_handler(context):
    """
    Validate the generated response against safety and quality guardrails.

    Checks (LLM-powered via qwen2.5:3b, with rule-based fallback):
      1. Lesson-only scope     — response stays within lesson content
      2. Grounded response     — claims backed by retrieved chunks
      3. Confidence check      — no hallucination / uncertainty phrases
      4. Readability rules     — dyslexia-friendly language
      5. No diagnosis claims   — no medical / clinical statements
      6. Quiz structure        — structural validation (rule-based)
      7. Assessment score      — score in 0-100 range (rule-based)

    Reads from context:
        context.intermediate_results["explanation"]
        context.retrieved_chunks
        context.intermediate_results["quiz"]
        context.intermediate_results["assessment"]
        context.intermediate_results["recommendations"]

    Writes to context:
        context.intermediate_results["guardrails_result"]
    """
    try:
        explanation = context.intermediate_results.get("explanation", "")
        chunks = context.retrieved_chunks or []
        quiz = context.intermediate_results.get("quiz", {})
        assessment = context.intermediate_results.get("assessment", {})
        recommendations = context.intermediate_results.get("recommendations", {})

        if _ENGINE_AVAILABLE:
            result = _engine.run_all_checks(
                response_text=explanation,
                lesson_chunks=chunks,
                quiz=quiz or None,
                assessment=assessment or None,
                recommendations=recommendations or None,
            )
        else:
            result = _rule_based_fallback(
                explanation, chunks, quiz, assessment, recommendations
            )

        result["validation_timestamp"] = str(context.timestamp)

        if result["passed"]:
            logger.info("Response passed all guardrails validation")
        else:
            logger.warning("Response failed guardrails: %s", result["issues"])

        return result

    except Exception as exc:
        logger.error("Error validating guardrails: %s", exc)
        raise


# ---------------------------------------------------------------------------
# Rule-based fallback (used only when GuardrailsEngine cannot be imported)
# ---------------------------------------------------------------------------

def _rule_based_fallback(explanation, chunks, quiz, assessment, recommendations):
    issues = []
    warnings = []

    # Groundedness
    if explanation and not chunks:
        warnings.append("Response generated without source content — ensure it's accurate")

    # No medical claims
    medical_keywords = [
        "dyslexia diagnosis", "diagnosed with dyslexia",
        "treatment for dyslexia", "cure for dyslexia",
        "medication", "prescribe", "medical condition",
    ]
    lower = explanation.lower() if explanation else ""
    for kw in medical_keywords:
        if kw in lower:
            issues.append(f"Found potentially clinical claim: '{kw}'")

    # Content appropriateness
    for word in ["violence", "explicit", "harmful", "dangerous"]:
        if word in lower:
            issues.append(f"Found potentially inappropriate content: '{word}'")

    # Length sanity
    if explanation and len(explanation) < 50:
        warnings.append("Response is very brief — consider providing more detail")
    elif explanation and len(explanation) > 5000:
        warnings.append("Response is very long — consider breaking into sections")

    # Quiz structure
    if quiz:
        for q in quiz.get("questions", []):
            if not q.get("question") or not q.get("options"):
                issues.append("Invalid quiz question structure")

    # Assessment score
    if assessment:
        score = assessment.get("percentage", 0)
        if not (0 <= score <= 100):
            issues.append(f"Invalid assessment score: {score}")

    # Recommendations count
    if recommendations:
        recs = recommendations.get("recommendations", [])
        if 0 < len(recs) < 3:
            warnings.append("Only a few recommendations available")

    return {"passed": len(issues) == 0, "issues": issues, "warnings": warnings}
