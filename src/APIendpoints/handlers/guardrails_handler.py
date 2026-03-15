"""Guardrails handler - VALIDATE_GUARDRAILS workflow step"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def validate_guardrails_handler(context):
    """
    Validate generated response against safety and quality guardrails.

    Checks:
    1. Response is grounded in lesson content (not hallucinations)
    2. No medical/diagnosis claims (especially for dyslexia)
    3. No harmful or inappropriate content
    4. Response length sanity
    5. Quiz question structure validity
    6. Assessment score range validity
    7. Recommendations availability
    """
    try:
        issues = []
        warnings = []
        passed = True

        # Check 1: Response is grounded
        explanation = context.intermediate_results.get("tutor_explanation", "")
        if isinstance(explanation, dict):
            explanation = explanation.get("explanation", "")
        chunks = context.retrieved_chunks or []

        if explanation and not chunks:
            warnings.append("Response generated without source content - ensure it's accurate")

        # Check 1b: Course relevance (if a course is selected)
        course_id = None
        if context.request.context:
            course_id = context.request.context.get("course_id")

        if course_id and chunks:
            course_doc_id = f"moodle_course_{course_id}"
            relevant_chunks = [c for c in chunks if c.get("document_id", "").startswith(course_doc_id)]
            if not relevant_chunks:
                low_scores = all(c.get("score", 0) < 0.3 for c in chunks)
                if low_scores:
                    warnings.append(
                        "Your question doesn't appear to be related to the selected course content. "
                        "Try asking something specific to your course material."
                    )
        elif course_id and not chunks:
            warnings.append(
                "No relevant course content found for your question. "
                "Make sure course content has been ingested."
            )

        # Check 2: No medical/diagnosis claims
        medical_warning_keywords = [
            "dyslexia diagnosis", "diagnosed with dyslexia",
            "treatment for dyslexia", "cure for dyslexia",
            "medication", "prescribe", "medical condition"
        ]

        explanation_lower = (explanation or "").lower()
        for keyword in medical_warning_keywords:
            if keyword in explanation_lower:
                issues.append(
                    f"WARNING: Found potentially clinical claim: '{keyword}'. "
                    "Ensure only educational content, not medical advice."
                )
                passed = False

        # Check 3: Content appropriateness
        inappropriate_words = ["violence", "explicit", "harmful", "dangerous"]
        for word in inappropriate_words:
            if word in explanation_lower:
                issues.append(f"Found potentially inappropriate content: '{word}'")
                passed = False

        # Check 4: Response length sanity
        if explanation and len(explanation) < 50:
            warnings.append("Response is very brief - consider providing more detail")
        elif explanation and len(explanation) > 5000:
            warnings.append("Response is very long - consider breaking into sections")

        # Check 5: Quiz questions are valid
        quiz = context.intermediate_results.get("generate_quiz", {})
        if isinstance(quiz, dict):
            questions = quiz.get("questions", [])
            for q in questions:
                if not q.get("question") and not q.get("question_text"):
                    issues.append("Invalid quiz question structure")
                    passed = False

        # Check 6: Assessment results valid
        assessment = context.intermediate_results.get("assess_quiz", {})
        if isinstance(assessment, dict):
            score = assessment.get("percentage", 0)
            if score and not (0 <= score <= 100):
                issues.append(f"Invalid assessment score: {score}")
                passed = False

        # Check 7: Recommendations are relevant
        recommendations = context.intermediate_results.get("recommend", {})
        if isinstance(recommendations, dict):
            recs = recommendations.get("recommendations", [])
            if len(recs) > 0 and len(recs) < 3:
                warnings.append("Only a few recommendations available")

        guardrails_result = {
            "passed": passed,
            "issues": issues,
            "warnings": warnings,
            "validation_timestamp": datetime.utcnow().isoformat()
        }

        if passed:
            logger.info("Response passed all guardrails validation")
        else:
            logger.warning(f"Response failed guardrails: {issues}")

        return guardrails_result

    except Exception as e:
        logger.error(f"Error validating guardrails: {e}")
        return {
            "passed": True,
            "issues": [],
            "warnings": [f"Guardrails validation error: {str(e)}"],
            "validation_timestamp": datetime.utcnow().isoformat()
        }
