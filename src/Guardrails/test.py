"""Quick smoke test for the GuardrailsEngine using qwen2.5:3b.
Run from the project root:
    python src/Guardrails/test.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Guardrails.guardrails_engine import GuardrailsEngine

engine = GuardrailsEngine()

result = engine.run_all_checks(
    response_text="The student is diagnosed with dyslexia and needs treatment.",
    lesson_chunks=[{"content": "Dyslexia can affect reading and spelling."}],
)

print("Passed:", result["passed"])
print("Issues:", result["issues"])
print("Warnings:", result["warnings"])
print("Details:", result["check_details"])
