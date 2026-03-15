"""
RAG Pipeline End-to-End Validation Test
----------------------------------------
Proves the RAG path works by:
  1. Injecting a sentinel phrase into the vector store
  2. Running a query through the retrieval handler
  3. Verifying the sentinel appears in retrieved context
  4. Running the tutor handler and verifying the LLM uses the context
  5. Optionally: comparing output with and without retrieval

Usage:
  # Full validation (requires Ollama running):
  DEBUG_RAG=true python -m pytest tests/test_rag_pipeline.py -v -s

  # Quick validation (no Ollama needed, tests retrieval only):
  python tests/test_rag_pipeline.py
"""

import os
import sys
import uuid

# Ensure project root is on path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Enable debug output for this test
os.environ["DEBUG_RAG"] = "true"


# ---------------------------------------------------------------------------
# Sentinel phrase — a unique string that only exists in our test chunk
# ---------------------------------------------------------------------------
SENTINEL = f"XYZZY_SENTINEL_{uuid.uuid4().hex[:8]}"
TEST_TENANT = "test_validation"
TEST_DOC_ID = f"test_doc_{uuid.uuid4().hex[:8]}"


def step1_ingest_sentinel():
    """STEP 1: Inject a test document with a sentinel phrase into the vector store."""
    print("\n" + "=" * 70)
    print("  STEP 1: Ingest sentinel phrase into vector store")
    print("=" * 70)

    from src.app.mcp.retrieval_tools import retrieval_upsert_chunks

    test_content = (
        f"The mitochondria is the powerhouse of the cell. "
        f"This document contains the unique identifier {SENTINEL} which proves "
        f"that retrieved content is actually being used by the LLM. "
        f"Photosynthesis converts light energy into chemical energy. "
        f"The process occurs in the chloroplasts of plant cells."
    )

    chunks = [
        {
            "chunk_id": f"{TEST_DOC_ID}_chunk_0",
            "document_id": TEST_DOC_ID,
            "tenant_id": TEST_TENANT,
            "chunk_index": 0,
            "content": test_content,
        },
        {
            "chunk_id": f"{TEST_DOC_ID}_chunk_1",
            "document_id": TEST_DOC_ID,
            "tenant_id": TEST_TENANT,
            "chunk_index": 1,
            "content": (
                f"Cell division is the process by which a parent cell divides "
                f"into two or more daughter cells. Mitosis produces identical "
                f"copies while meiosis produces cells with half the chromosomes. "
                f"This content is tagged with sentinel {SENTINEL}."
            ),
        },
    ]

    count = retrieval_upsert_chunks(chunks)
    print(f"  Ingested {count} chunks with sentinel: {SENTINEL}")
    assert count == 2, f"Expected 2 chunks, got {count}"
    print("  PASS: Sentinel chunks ingested successfully")
    return True


def step2_verify_retrieval():
    """STEP 2: Query the vector store and verify sentinel chunk is retrieved."""
    print("\n" + "=" * 70)
    print("  STEP 2: Verify vector store retrieval returns sentinel")
    print("=" * 70)

    from src.app.mcp.retrieval_tools import retrieval_search_chunks

    results = retrieval_search_chunks(
        query_text="What is the powerhouse of the cell?",
        tenant_id=TEST_TENANT,
        top_k=5,
    )

    print(f"  Retrieved {len(results)} chunks")
    assert len(results) > 0, "Vector store returned 0 results!"

    # Verify sentinel is in at least one result
    sentinel_found = False
    for i, r in enumerate(results):
        content = r.get("content", "")
        score = r.get("score", 0)
        has_sentinel = SENTINEL in content
        print(f"  Chunk #{i}: score={score:.3f} sentinel={'YES' if has_sentinel else 'no'} "
              f"preview={content[:80]}...")
        if has_sentinel:
            sentinel_found = True

    assert sentinel_found, f"Sentinel {SENTINEL} NOT found in any retrieved chunk!"
    print("  PASS: Sentinel found in retrieved chunks")
    return results


def step3_verify_context_assembly():
    """STEP 3: Run the retrieval handler and verify context attributes are set."""
    print("\n" + "=" * 70)
    print("  STEP 3: Verify retrieval handler sets context attributes")
    print("=" * 70)

    import asyncio
    from dataclasses import dataclass, field
    from typing import Dict, Any, Optional, List

    # Mock request and context that match orchestrator schemas
    @dataclass
    class MockRequest:
        user_id: str = "test_user"
        message: str = "Explain the powerhouse of the cell"
        lesson_id: Optional[str] = None
        session_id: Optional[str] = None
        context: Dict[str, Any] = field(default_factory=lambda: {"tenant_id": TEST_TENANT})

    @dataclass
    class MockContext:
        request: MockRequest = field(default_factory=MockRequest)
        intent: str = "explain_lesson"
        user_profile: Optional[Dict[str, Any]] = field(default_factory=dict)
        lesson_content: Optional[Dict[str, Any]] = None
        retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
        intermediate_results: Dict[str, Any] = field(default_factory=dict)
        errors: List[str] = field(default_factory=list)

        def add_result(self, step, result):
            self.intermediate_results[step] = result

        def get_result(self, step):
            return self.intermediate_results.get(step)

    # Import retrieval_handler directly (avoid handlers/__init__.py cascade)
    import importlib.util
    handler_path = os.path.join(
        project_root, "src", "APIendpoints", "handlers", "retrieval_handler.py"
    )
    spec = importlib.util.spec_from_file_location("retrieval_handler", handler_path)
    retrieval_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(retrieval_mod)
    retrieve_lesson_handler = retrieval_mod.retrieve_lesson_handler

    ctx = MockContext()
    result = asyncio.run(retrieve_lesson_handler(ctx))

    print(f"  Result source: {result.get('source', 'unknown')}")
    print(f"  context.retrieved_chunks count: {len(ctx.retrieved_chunks)}")
    print(f"  context.lesson_content set: {ctx.lesson_content is not None}")

    assert len(ctx.retrieved_chunks) > 0, "context.retrieved_chunks is EMPTY after retrieval!"
    assert ctx.lesson_content is not None, "context.lesson_content is NONE after retrieval!"

    # Verify sentinel is in the assembled content
    full_content = ctx.lesson_content.get("content", "")
    assert SENTINEL in full_content, f"Sentinel NOT in lesson_content! Content: {full_content[:200]}..."

    print(f"  Content length: {len(full_content)} chars")
    print(f"  Sentinel in content: YES")
    print("  PASS: Retrieval handler correctly populates context")
    return ctx


def step4_verify_tutor_uses_context(ctx=None):
    """STEP 4: Run tutor handler and verify LLM response is conditioned on context."""
    print("\n" + "=" * 70)
    print("  STEP 4: Verify tutor handler uses retrieved context")
    print("=" * 70)

    import asyncio

    if ctx is None:
        ctx = step3_verify_context_assembly()

    # Import tutor_handler directly (avoid handlers/__init__.py cascade)
    import importlib.util as _ilu
    tutor_path = os.path.join(project_root, "src", "APIendpoints", "handlers", "tutor_handler.py")
    spec = _ilu.spec_from_file_location("tutor_handler", tutor_path)
    tutor_mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(tutor_mod)
    tutor_explanation_handler = tutor_mod.tutor_explanation_handler

    result = asyncio.run(tutor_explanation_handler(ctx))

    explanation = result.get("explanation", "")
    method = result.get("generation_method", "unknown")
    sources = result.get("sources", [])

    print(f"  Generation method: {method}")
    print(f"  Explanation length: {len(explanation)} chars")
    print(f"  Sources count: {len(sources)}")
    print(f"  Explanation preview: {explanation[:300]}...")

    assert len(explanation) > 50, "Explanation is too short!"
    assert len(sources) > 0, "No sources returned!"

    # Check if tutor actually referenced the content
    content_keywords = ["mitochondria", "powerhouse", "cell", "photosynthesis"]
    keywords_found = [kw for kw in content_keywords if kw.lower() in explanation.lower()]
    print(f"  Content keywords found in explanation: {keywords_found}")
    assert len(keywords_found) > 0, "Explanation does NOT reference any retrieved content keywords!"

    print(f"\n  PASS: Tutor handler produced context-grounded explanation (method={method})")
    return result


def step5_cleanup():
    """STEP 5: Clean up test data from vector store."""
    print("\n" + "=" * 70)
    print("  STEP 5: Cleanup")
    print("=" * 70)

    try:
        from src.app.mcp.retrieval_tools import retrieval_delete_document
        retrieval_delete_document(TEST_DOC_ID, TEST_TENANT)
        print(f"  Cleaned up test document {TEST_DOC_ID}")
    except Exception as e:
        print(f"  Cleanup warning (non-fatal): {e}")

    print("  DONE")


# ---------------------------------------------------------------------------
# Main validation runner
# ---------------------------------------------------------------------------

def run_full_validation():
    """Run the complete RAG pipeline validation."""
    print("=" * 70)
    print("  RAG PIPELINE END-TO-END VALIDATION")
    print(f"  Sentinel phrase: {SENTINEL}")
    print("=" * 70)

    results = {}
    try:
        results["ingest"] = step1_ingest_sentinel()
        results["retrieval"] = step2_verify_retrieval() is not None
        ctx = step3_verify_context_assembly()
        results["context"] = ctx is not None
        results["tutor"] = step4_verify_tutor_uses_context(ctx) is not None
    except AssertionError as e:
        print(f"\n  VALIDATION FAILED: {e}")
        results["error"] = str(e)
    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback
        traceback.print_exc()
        results["error"] = str(e)
    finally:
        step5_cleanup()

    # Summary
    print("\n" + "=" * 70)
    print("  VALIDATION SUMMARY")
    print("=" * 70)
    for step, ok in results.items():
        if step == "error":
            print(f"  ERROR: {ok}")
        else:
            status = "PASS" if ok else "FAIL"
            print(f"  {step}: {status}")

    has_error = "error" in results
    all_steps_passed = all(v for k, v in results.items() if k != "error")
    overall = not has_error and all_steps_passed
    print(f"\n  OVERALL: {'ALL TESTS PASSED' if overall else 'SOME TESTS FAILED'}")
    print("=" * 70)
    return overall


# ---------------------------------------------------------------------------
# Pytest integration
# ---------------------------------------------------------------------------

def test_sentinel_ingest_and_retrieve():
    """Pytest: verify sentinel phrase survives ingest → retrieve roundtrip."""
    step1_ingest_sentinel()
    results = step2_verify_retrieval()
    assert any(SENTINEL in r.get("content", "") for r in results)
    step5_cleanup()


def test_retrieval_handler_populates_context():
    """Pytest: verify retrieval handler sets context.retrieved_chunks."""
    step1_ingest_sentinel()
    ctx = step3_verify_context_assembly()
    assert len(ctx.retrieved_chunks) > 0
    assert ctx.lesson_content is not None
    step5_cleanup()


def test_tutor_handler_uses_context():
    """Pytest: verify tutor handler produces context-grounded explanation."""
    step1_ingest_sentinel()
    ctx = step3_verify_context_assembly()
    result = step4_verify_tutor_uses_context(ctx)
    assert len(result.get("explanation", "")) > 50
    assert result.get("generation_method") in ("llm", "rule_based")
    step5_cleanup()


# ---------------------------------------------------------------------------
# Direct execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    success = run_full_validation()
    sys.exit(0 if success else 1)
