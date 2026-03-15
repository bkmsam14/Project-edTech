"""
Moodle Content Ingestion Pipeline
----------------------------------
Extracts course content from Moodle and ingests it into the NeuroLearn
vector store (ChromaDB) so the RAG pipeline can retrieve it.

Pipeline:
  1. Login to Moodle (browser automation)
  2. Fetch all courses
  3. For each course: scrape sections, activities, page content
  4. Chunk the text
  5. Embed and upsert into ChromaDB via retrieval_upsert_chunks()
  6. Optionally save metadata to Supabase via content_save_document()

Usage:
  python -m src.mcp_moodle.ingest_moodle_content

Environment:
  MOODLE_URL       - Moodle instance URL (default: https://moodle.medtech.tn)
  MOODLE_TOKEN     - Pre-set session cookie (optional, skips login if set)
  DEBUG_RAG=true   - Enable verbose debug output
"""

import os
import sys
import uuid

# Ensure project root is on Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

DEBUG_RAG = os.environ.get("DEBUG_RAG", "").lower() in ("1", "true", "yes")


def _debug(msg: str):
    if DEBUG_RAG:
        print(f"[DEBUG_RAG][ingest] {msg}")


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, max_chunk_chars: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks of roughly max_chunk_chars."""
    if not text or len(text.strip()) < 20:
        return []

    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current = ""

    for sentence in sentences:
        candidate = (current + ". " + sentence).strip() if current else sentence.strip()
        if len(candidate) > max_chunk_chars and current:
            chunks.append(current.strip())
            # Overlap: keep last N chars
            current = current[-overlap:] + " " + sentence if overlap else sentence
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def ingest_course(client, course_id: int, course_name: str, tenant_id: str = "default"):
    """
    Scrape one course from Moodle and upsert its content into the vector store.

    Returns:
        dict with ingestion stats.
    """
    from src.app.mcp.retrieval_tools import retrieval_upsert_chunks

    print(f"\n  Ingesting course: {course_name} (id={course_id})")

    # Scrape course structure
    course_data = client.get_course_content(course_id)
    sections = course_data.get("sections", [])
    _debug(f"  Found {len(sections)} sections")

    document_id = f"moodle_course_{course_id}"
    all_chunks = []
    chunk_index = 0

    for sec in sections:
        sec_title = sec.get("section_title", "")
        activities = sec.get("activities", [])

        for act in activities:
            act_name = act.get("name", "")
            act_type = act.get("type", "unknown")
            inline_content = act.get("content", "")
            act_url = act.get("url", "")

            # Collect text from inline content
            text = ""
            if inline_content:
                text = inline_content

            # For Page resources, fetch full content
            if act_type == "page" and act_url:
                try:
                    page_text = client.get_page_content(act_url)
                    if page_text:
                        text = page_text
                        _debug(f"  Fetched page: {act_name} ({len(page_text)} chars)")
                except Exception as e:
                    _debug(f"  Failed to fetch page {act_name}: {e}")

            if not text or len(text.strip()) < 20:
                continue

            # Prefix with context for better retrieval
            prefixed_text = f"Course: {course_name}\nSection: {sec_title}\nTopic: {act_name}\n\n{text}"

            # Chunk the text
            text_chunks = chunk_text(prefixed_text, max_chunk_chars=500)

            for chunk_text_piece in text_chunks:
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "tenant_id": tenant_id,
                    "chunk_index": chunk_index,
                    "content": chunk_text_piece,
                })
                chunk_index += 1

    # Also ingest grades as additional context
    try:
        grade_data = client.get_grades(course_id)
        grade_items = grade_data.get("items", [])
        if grade_items:
            grade_text = f"Course: {course_name}\nGrade Summary:\n"
            for item in grade_items:
                grade_display = item.get("grade", "-")
                pct = item.get("percentage", "")
                grade_text += f"  - {item.get('item', 'Unknown')}: {grade_display}"
                if pct:
                    grade_text += f" ({pct})"
                grade_text += "\n"

            for chunk_text_piece in chunk_text(grade_text):
                chunk_id = f"{document_id}_grades_chunk_{chunk_index}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "tenant_id": tenant_id,
                    "chunk_index": chunk_index,
                    "content": chunk_text_piece,
                })
                chunk_index += 1
    except Exception as e:
        _debug(f"  Grade ingestion failed for {course_name}: {e}")

    # Upsert into vector store
    if all_chunks:
        print(f"    Embedding and upserting {len(all_chunks)} chunks...")
        count = retrieval_upsert_chunks(all_chunks)
        print(f"    Done: {count} chunks indexed")
    else:
        print(f"    No content to ingest for {course_name}")

    return {
        "course_id": course_id,
        "course_name": course_name,
        "sections_scraped": len(sections),
        "chunks_indexed": len(all_chunks),
    }


def ingest_all_courses(client, tenant_id: str = "default") -> list[dict]:
    """Ingest all enrolled courses."""
    courses = client.get_enrolled_courses()
    print(f"\nFound {len(courses)} enrolled courses")

    results = []
    for course in courses:
        cid = course.get("id")
        if not cid:
            continue
        try:
            result = ingest_course(client, cid, course["fullname"], tenant_id)
            results.append(result)
        except Exception as e:
            print(f"    ERROR ingesting {course['fullname']}: {e}")
            results.append({
                "course_id": cid,
                "course_name": course["fullname"],
                "error": str(e),
            })

    return results


# ---------------------------------------------------------------------------
# Standalone: ingest content from plain text / file (no Moodle needed)
# ---------------------------------------------------------------------------

def ingest_text(
    text: str,
    document_id: str = None,
    title: str = "Manual Content",
    tenant_id: str = "default",
) -> int:
    """
    Ingest arbitrary text into the vector store.
    Useful for testing the RAG pipeline without Moodle.

    Returns:
        Number of chunks ingested.
    """
    from src.app.mcp.retrieval_tools import retrieval_upsert_chunks

    document_id = document_id or f"manual_{uuid.uuid4().hex[:8]}"
    prefixed = f"Document: {title}\n\n{text}"
    text_chunks = chunk_text(prefixed, max_chunk_chars=500)

    if not text_chunks:
        return 0

    chunks = [
        {
            "chunk_id": f"{document_id}_chunk_{i}",
            "document_id": document_id,
            "tenant_id": tenant_id,
            "chunk_index": i,
            "content": c,
        }
        for i, c in enumerate(text_chunks)
    ]

    count = retrieval_upsert_chunks(chunks)
    print(f"Ingested {count} chunks for '{title}' (doc={document_id})")
    return count


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """Interactive ingestion from Moodle."""
    # Import Moodle tools (these are in the same directory)
    moodle_dir = os.path.dirname(__file__)
    if moodle_dir not in sys.path:
        sys.path.insert(0, moodle_dir)

    from moodle_login import get_session_cookie
    from moodle_client import MoodleClient

    print("=" * 60)
    print("  Moodle Content Ingestion Pipeline")
    print("=" * 60)

    # Check if session cookie is pre-set
    token = os.environ.get("MOODLE_TOKEN", "")
    if token and token != "paste_your_MoodleSession_cookie_here":
        print("  Using MOODLE_TOKEN from environment")
    else:
        print("\n  Moodle Login Required")
        email = input("  Email   : ").strip()
        password = input("  Password: ").strip()
        if not email or not password:
            print("  ERROR: Credentials required")
            return
        print("  [Logging in...] A browser window will open briefly.")
        try:
            token = get_session_cookie(email, password)
            print("  Login successful!")
        except Exception as e:
            print(f"  Login failed: {e}")
            return

    client = MoodleClient(token)
    results = ingest_all_courses(client, tenant_id="default")

    print("\n" + "=" * 60)
    print("  INGESTION SUMMARY")
    print("=" * 60)
    total_chunks = 0
    for r in results:
        n = r.get("chunks_indexed", 0)
        total_chunks += n
        status = f"{n} chunks" if not r.get("error") else f"ERROR: {r['error']}"
        print(f"  {r['course_name']}: {status}")
    print(f"\n  Total: {total_chunks} chunks indexed across {len(results)} courses")
    print("=" * 60)


if __name__ == "__main__":
    main()
