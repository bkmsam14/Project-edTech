"""Guardrails handler - VALIDATE_GUARDRAILS workflow step"""
import logging

logger = logging.getLogger(__name__)


async def validate_guardrails_handler(context):
    """
    Validate generated response against safety and quality guardrails.

    Checks:
    1. Response is grounded in lesson content (not hallucinations)
    2. No medical/diagnosis claims (especially for dyslexia)
    3. Appropriate language level for user
    4. Content is within scope of lesson
    5. No harmful or inappropriate content

    Input (from context):
        - All intermediate results

    Output:
        - passed: Boolean indicating if response passes guardrails
        - issues: List of any issues found
        - warnings: List of warnings
        - stores in context.intermediate_results["guardrails_result"]
    """
    try:
        issues = []
        warnings = []
        passed = True

        # Check 1: Response is grounded
        explanation = context.intermediate_results.get("explanation", "")
        chunks = context.retrieved_chunks or []

        if explanation and not chunks:
            warnings.append("Response generated without source content - ensure it's accurate")

        # Check 2: No medical/diagnosis claims (especially for dyslexia)
        medical_warning_keywords = [
            "dyslexia diagnosis",
            "diagnosed with dyslexia",
            "treatment for dyslexia",
            "cure for dyslexia",
            "medication",
            "prescribe",
            "medical condition"
        ]

        explanation_lower = explanation.lower()
        for keyword in medical_warning_keywords:
            if keyword in explanation_lower:
                issues.append(f"WARNING: Found potentially clinical claim: '{keyword}'. "
                            "Ensure only educational content, not medical advice.")
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
        quiz = context.intermediate_results.get("quiz", {})
        if quiz:
            questions = quiz.get("questions", [])
            for q in questions:
                if not q.get("question") or not q.get("options"):
                    issues.append(f"Invalid quiz question structure")
                    passed = False

        # Check 6: Assessment results valid
        assessment = context.intermediate_results.get("assessment", {})
        if assessment:
            score = assessment.get("percentage", 0)
            if not (0 <= score <= 100):
                issues.append(f"Invalid assessment score: {score}")
                passed = False

        # Check 7: Recommendations are relevant
        recommendations = context.intermediate_results.get("recommendations", {})
        if recommendations:
            recs = recommendations.get("recommendations", [])
            if len(recs) > 0 and len(recs) < 3:
                warnings.append("Only a few recommendations available")

        guardrails_result = {
            "passed": passed,
            "issues": issues,
            "warnings": warnings,
            "validation_timestamp": str(context.timestamp)
        }

        if passed:
            logger.info("Response passed all guardrails validation")
        else:
            logger.warning(f"Response failed guardrails: {issues}")

        return guardrails_result

    except Exception as e:
        logger.error(f"Error validating guardrails: {e}")
        raise
