"""
LLM-powered Guardrails Engine using qwen2.5:3b via Ollama.

Checks (from architecture):
  1. Lesson-only scope     — response stays within lesson content
  2. Grounded response     — claims are backed by retrieved chunks
  3. Confidence check      — detects hallucination / uncertainty phrases
  4. Readability rules     — appropriate for dyslexic learners
  5. No diagnosis claims   — no medical / clinical statements

Each check returns {"passed": bool, "reason": str} or {"passed": bool, "warnings": list}.
GuardrailsEngine.run_all_checks() aggregates them into a single result dict.
"""

import logging
from typing import Any, Dict, List, Optional

from ollama import chat

logger = logging.getLogger(__name__)

GUARDRAILS_MODEL = "qwen2.5:3b"


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _llm(prompt: str, model: str = GUARDRAILS_MODEL) -> Optional[str]:
    """Send a prompt to the guardrail model and return the raw text reply."""
    try:
        response = chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"].strip()
    except Exception as exc:
        logger.error("Guardrail LLM call failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_lesson_scope(response_text: str, chunk_texts: List[str]) -> Dict[str, Any]:
    """
    Check 1 — Lesson-only scope.
    Verifies the response discusses only topics present in the lesson chunks.
    """
    if not response_text:
        return {"passed": True, "reason": "No response to check"}
    if not chunk_texts:
        return {"passed": True, "reason": "No lesson context available — scope check skipped"}

    lesson_summary = "\n".join(chunk_texts[:3])[:1500]

    prompt = f"""You are a content-scope validator for an educational AI.

LESSON CONTENT (source of truth):
{lesson_summary}

AI RESPONSE TO CHECK:
{response_text[:1000]}

Task: Does the AI response ONLY discuss topics that appear in the lesson content above?
Answer with ONLY: YES or NO
Then on a new line, one short reason (max 15 words)."""

    raw = _llm(prompt)
    if raw is None:
        return {"passed": True, "reason": "Scope check skipped (model unavailable)"}

    lines = raw.strip().splitlines()
    passed = lines[0].strip().upper().startswith("YES")
    reason = lines[1].strip() if len(lines) > 1 else raw[:120]
    return {"passed": passed, "reason": reason}


def check_groundedness(response_text: str, chunk_texts: List[str]) -> Dict[str, Any]:
    """
    Check 2 — Grounded response.
    Verifies main claims in the response are supported by the lesson chunks.
    """
    if not response_text or not chunk_texts:
        return {"passed": True, "reason": "Groundedness check skipped (missing data)"}

    chunks_text = "\n---\n".join(chunk_texts[:4])[:2000]

    prompt = f"""You are a fact-grounding validator for an educational AI.

SOURCE LESSON CHUNKS:
{chunks_text}

AI RESPONSE:
{response_text[:800]}

Task: Are the main claims in the AI response supported by the source lesson chunks above?
Answer with ONLY: YES or NO
Then on a new line, one short reason (max 15 words)."""

    raw = _llm(prompt)
    if raw is None:
        return {"passed": True, "reason": "Groundedness check skipped (model unavailable)"}

    lines = raw.strip().splitlines()
    passed = lines[0].strip().upper().startswith("YES")
    reason = lines[1].strip() if len(lines) > 1 else raw[:120]
    return {"passed": passed, "reason": reason}


def check_no_diagnosis_claims(response_text: str) -> Dict[str, Any]:
    """
    Check 3 — No medical/diagnosis claims.
    Blocks responses that make clinical or diagnostic statements.
    Fast rule-based pre-scan, then LLM for subtle cases.
    """
    if not response_text:
        return {"passed": True, "reason": "No response to check"}

    # Fast keyword pre-scan
    medical_keywords = [
        "dyslexia diagnosis", "diagnosed with dyslexia",
        "treatment for dyslexia", "cure for dyslexia",
        "medication", "prescribe", "medical condition",
        "clinical", "therapist recommends", "doctor",
    ]
    lower = response_text.lower()
    for kw in medical_keywords:
        if kw in lower:
            return {"passed": False, "reason": f"Medical/clinical claim found: '{kw}'"}

    # LLM double-check for subtle cases
    prompt = f"""You are a safety validator for an educational AI used by students with dyslexia.

AI RESPONSE:
{response_text[:800]}

Task: Does this response make any medical diagnosis, clinical recommendation, or claim
to treat or cure a learning disability?
Answer with ONLY: YES or NO
Then on a new line, one short reason (max 15 words)."""

    raw = _llm(prompt)
    if raw is None:
        return {"passed": True, "reason": "Diagnosis check skipped (model unavailable)"}

    lines = raw.strip().splitlines()
    has_claim = lines[0].strip().upper().startswith("YES")
    reason = lines[1].strip() if len(lines) > 1 else raw[:120]
    return {"passed": not has_claim, "reason": reason}


def check_readability(response_text: str) -> Dict[str, Any]:
    """
    Check 4 — Readability rules for dyslexic learners.
    Returns {"passed": bool, "warnings": list[str]}.
    """
    if not response_text:
        return {"passed": True, "warnings": []}

    warnings: List[str] = []

    # Rule-based: sentence length
    sentences = [
        s.strip()
        for s in response_text.replace("?", ".").replace("!", ".").split(".")
        if s.strip()
    ]
    avg_words = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    if avg_words > 25:
        warnings.append("Sentences are too long — aim for under 20 words each")

    # Rule-based: total length
    if len(response_text) > 800:
        warnings.append("Response is long — consider breaking into short bullet points")

    # LLM readability check
    prompt = f"""You are a readability expert for dyslexic learners (ages 10–18).

TEXT TO EVALUATE:
{response_text[:600]}

Task: Is this text simple and easy to read for a student with dyslexia?
Answer with ONLY: YES or NO
Then on a new line: one brief improvement suggestion (max 15 words), or "None"."""

    raw = _llm(prompt)
    if raw:
        lines = raw.strip().splitlines()
        is_readable = lines[0].strip().upper().startswith("YES")
        suggestion = lines[1].strip() if len(lines) > 1 else ""
        if not is_readable and suggestion and suggestion.lower() != "none":
            warnings.append(f"Readability suggestion: {suggestion}")

    return {"passed": len(warnings) == 0, "warnings": warnings}


def check_confidence(response_text: str) -> Dict[str, Any]:
    """
    Check 5 — Confidence / hallucination detection.
    Flags uncertainty phrases that suggest the model is guessing.
    """
    if not response_text:
        return {"passed": True, "reason": "No response to check"}

    uncertainty_phrases = [
        "i think", "i believe", "i'm not sure", "probably", "maybe",
        "might be", "could be", "as far as i know", "i'm guessing",
        "not certain", "i suppose", "i assume",
    ]
    lower = response_text.lower()
    found = [p for p in uncertainty_phrases if p in lower]

    if found:
        return {
            "passed": False,
            "reason": f"Uncertainty phrases detected: {', '.join(found[:3])}",
        }
    return {"passed": True, "reason": "No uncertainty indicators found"}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class GuardrailsEngine:
    """
    Aggregates all guardrail checks into a single validation pass.
    Uses qwen2.5:3b for LLM-powered checks via Ollama.

    Usage:
        engine = GuardrailsEngine()
        result = engine.run_all_checks(
            response_text="...",
            lesson_chunks=[{"content": "..."}],
        )
        # result: {"passed": bool, "issues": [...], "warnings": [...], "check_details": {...}}
    """

    def __init__(self, model: str = GUARDRAILS_MODEL):
        self.model = model

    def run_all_checks(
        self,
        response_text: str,
        lesson_chunks: Optional[List[Any]] = None,
        quiz: Optional[Dict[str, Any]] = None,
        assessment: Optional[Dict[str, Any]] = None,
        recommendations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run all guardrail checks and return an aggregated result.

        Args:
            response_text:   The generated explanation / answer to validate.
            lesson_chunks:   Retrieved lesson chunks (list of dicts or strings).
            quiz:            Quiz dict (optional) for structural validation.
            assessment:      Assessment dict (optional) for score validation.
            recommendations: Recommendations dict (optional) for quantity check.

        Returns:
            {
                "passed":        bool,
                "issues":        list[str],   # blocking failures
                "warnings":      list[str],   # non-blocking notices
                "check_details": dict,        # per-check breakdown
            }
        """
        issues: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {}

        # Normalise lesson chunks to plain strings
        chunk_texts: List[str] = []
        for chunk in lesson_chunks or []:
            if isinstance(chunk, dict):
                chunk_texts.append(chunk.get("content", chunk.get("text", "")))
            elif isinstance(chunk, str):
                chunk_texts.append(chunk)

        # ------------------------------------------------------------------
        # Check 1: Lesson-only scope
        # ------------------------------------------------------------------
        if response_text:
            scope = check_lesson_scope(response_text, chunk_texts)
            details["scope"] = scope
            if not scope["passed"]:
                issues.append(f"Out-of-scope response: {scope['reason']}")

        # ------------------------------------------------------------------
        # Check 2: Groundedness
        # ------------------------------------------------------------------
        if response_text and chunk_texts:
            ground = check_groundedness(response_text, chunk_texts)
            details["groundedness"] = ground
            if not ground["passed"]:
                warnings.append(f"Response may not be grounded: {ground['reason']}")
        elif response_text and not chunk_texts:
            warnings.append("Response generated without lesson source chunks")

        # ------------------------------------------------------------------
        # Check 3: No diagnosis claims
        # ------------------------------------------------------------------
        if response_text:
            diag = check_no_diagnosis_claims(response_text)
            details["diagnosis"] = diag
            if not diag["passed"]:
                issues.append(f"Medical/diagnosis claim detected: {diag['reason']}")

        # ------------------------------------------------------------------
        # Check 4: Readability
        # ------------------------------------------------------------------
        if response_text:
            readability = check_readability(response_text)
            details["readability"] = readability
            warnings.extend(readability["warnings"])

        # ------------------------------------------------------------------
        # Check 5: Confidence / hallucination
        # ------------------------------------------------------------------
        if response_text:
            confidence = check_confidence(response_text)
            details["confidence"] = confidence
            if not confidence["passed"]:
                warnings.append(f"Low-confidence response: {confidence['reason']}")

        # ------------------------------------------------------------------
        # Structural checks (quiz, assessment, recommendations)
        # ------------------------------------------------------------------
        if quiz:
            for q in quiz.get("questions", []):
                has_text = q.get("question") or q.get("question_text")
                if not has_text or not q.get("options"):
                    issues.append("Invalid quiz question structure")

        if assessment:
            score = assessment.get("percentage", 0)
            if not (0 <= score <= 100):
                issues.append(f"Invalid assessment score: {score}")

        if recommendations:
            recs = recommendations.get("recommendations", [])
            if 0 < len(recs) < 3:
                warnings.append("Only a few recommendations available")

        # ------------------------------------------------------------------
        # Final verdict
        # ------------------------------------------------------------------
        passed = len(issues) == 0

        if passed:
            logger.info("All guardrail checks passed")
        else:
            logger.warning("Guardrail checks FAILED: %s", issues)

        return {
            "passed": passed,
            "issues": issues,
            "warnings": warnings,
            "check_details": details,
        }
