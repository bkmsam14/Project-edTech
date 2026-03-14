"""
RAG-based Grade Discussion Chatbot with Ollama
-----------------------------------------------
True RAG implementation that:
  1. Asks for email/password
  2. Logs into Moodle via browser automation
  3. Fetches all your grades
  4. Creates vector embeddings and stores in ChromaDB
  5. Uses semantic search to retrieve relevant grade info
  6. Lets you discuss your grades with qwen2.5:3b using RAG

Requirements:
  - Ollama installed and running (https://ollama.com/download)
  - Model pulled: ollama pull qwen2.5:3b
  - ChromaDB for vector storage
"""

import sys
import ollama
import chromadb
from chromadb.utils import embedding_functions
from moodle_login import get_session_cookie
from moodle_client import MoodleClient, MoodleError

OLLAMA_MODEL = "qwen2.5:3b"
EMBEDDING_MODEL = "nomic-embed-text"  # Ollama embedding model


def fetch_all_grades(client: MoodleClient) -> dict:
    """Fetch profile, courses, and all grades."""
    print("\n[Fetching your data from Moodle...]")

    # Get profile
    profile = client.get_site_info()
    print(f"  ✓ Profile: {profile['full_name']}")

    # Get all courses
    courses = client.get_enrolled_courses()
    print(f"  ✓ Found {len(courses)} course(s)")

    # Get grades for each course
    all_grades = []
    for course in courses:
        if course["id"]:
            print(f"  ✓ Fetching grades for: {course['fullname']}")
            grade_data = client.get_grades(course["id"])
            all_grades.append({
                "course_id": course["id"],
                "course_name": course["fullname"],
                "overall_grade": course.get("grade", "N/A"),
                "items": grade_data.get("items", []),
            })

    return {
        "profile": profile,
        "courses": courses,
        "grades": all_grades,
    }


def create_grade_chunks(data: dict) -> list[dict]:
    """
    Create chunks of grade information for vector embedding.
    Each chunk is a logical piece of information (course overview, individual grades, etc.)
    """
    chunks = []
    profile = data["profile"]

    # Profile chunk
    chunks.append({
        "id": "profile",
        "text": f"Student Profile: {profile['full_name']}, Email: {profile['email']}",
        "metadata": {"type": "profile", "student": profile['full_name']},
    })

    # Course overview chunk
    course_overview = "Enrolled Courses:\n"
    for grade_info in data["grades"]:
        course_name = grade_info["course_name"]
        overall = grade_info["overall_grade"]
        course_overview += f"- {course_name}: Overall Grade {overall}\n"

    chunks.append({
        "id": "courses_overview",
        "text": course_overview,
        "metadata": {"type": "courses_overview"},
    })

    # Individual course chunks with detailed grades
    for idx, grade_info in enumerate(data["grades"]):
        course_name = grade_info["course_name"]
        course_id = grade_info["course_id"]
        overall = grade_info["overall_grade"]
        items = grade_info["items"]

        # Course summary chunk
        course_text = f"Course: {course_name}\nOverall Grade: {overall}\n\nDetailed Grades:\n"

        if items:
            for item in items:
                grade_display = item["grade"]
                if item["percentage"]:
                    grade_display += f" ({item['percentage']})"
                course_text += f"  • {item['item']}: {grade_display}\n"
        else:
            course_text += "  No detailed grade items available.\n"

        chunks.append({
            "id": f"course_{course_id}",
            "text": course_text,
            "metadata": {
                "type": "course_detail",
                "course_name": course_name,
                "course_id": course_id,
                "overall_grade": overall,
            },
        })

        # Individual grade item chunks (more granular for better retrieval)
        for item_idx, item in enumerate(items):
            item_text = (
                f"Course: {course_name}\n"
                f"Assignment/Item: {item['item']}\n"
                f"Grade: {item['grade']}"
            )
            if item["percentage"]:
                item_text += f"\nPercentage: {item['percentage']}"

            chunks.append({
                "id": f"course_{course_id}_item_{item_idx}",
                "text": item_text,
                "metadata": {
                    "type": "grade_item",
                    "course_name": course_name,
                    "course_id": course_id,
                    "item_name": item["item"],
                    "grade": item["grade"],
                },
            })

    return chunks


def setup_vector_db(chunks: list[dict]) -> chromadb.Collection:
    """Create ChromaDB collection and add grade chunks with embeddings."""
    print("\n[Setting up RAG vector database...]")

    # Create ChromaDB client (in-memory for this session)
    chroma_client = chromadb.Client()

    # Create embedding function using Ollama
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
        url="http://localhost:11434/api/embeddings",
    )

    # Create or get collection
    collection = chroma_client.create_collection(
        name="student_grades",
        embedding_function=ollama_ef,
        metadata={"description": "Student grade information for RAG"}
    )

    # Prepare data for insertion
    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # Add to collection
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"  ✓ Added {len(chunks)} chunks to vector database")
    return collection


def retrieve_relevant_context(collection: chromadb.Collection, query: str, n_results: int = 5) -> str:
    """Retrieve relevant grade information based on the user query."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    # Extract and format retrieved documents
    if results and results["documents"] and results["documents"][0]:
        retrieved_docs = results["documents"][0]
        context = "\n\n---\n\n".join(retrieved_docs)
        return context

    return "No relevant information found."


def chat_loop(collection: chromadb.Collection, student_name: str):
    """Interactive RAG-based chat loop with the LLM."""

    print("=" * 70)
    print("  RAG-based Grade Discussion Chatbot Ready!")
    print("=" * 70)
    print("\nType your questions about your grades. Type 'quit' to exit.")
    print("\nExample questions:")
    print("  - What are my grades?")
    print("  - Which course am I doing best in?")
    print("  - What should I focus on improving?")
    print("  - How did I do in [specific course]?")
    print("  - Show me my worst performing assignments")
    print("=" * 70)
    print()

    # Conversation history
    messages = []

    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting chatbot. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\n[Retrieving relevant information...]\n")

        # RAG: Retrieve relevant context based on the query
        retrieved_context = retrieve_relevant_context(collection, user_input, n_results=5)

        print(f"[Retrieved {len(retrieved_context.split('---'))} relevant chunks]\n")

        # Build messages with retrieved context
        current_messages = [
            {
                "role": "system",
                "content": (
                    f"You are a helpful academic advisor assistant for {student_name}. "
                    "Answer questions about their academic performance based on the provided grade information. "
                    "Provide encouragement and suggest areas for improvement.\n\n"
                    "RELEVANT GRADE INFORMATION:\n"
                    f"{retrieved_context}"
                ),
            },
        ] + messages + [
            {"role": "user", "content": user_input}
        ]

        print("[Generating response...]\n")

        # Get LLM response
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=current_messages,
            )

            assistant_reply = response.message.content

            # Add to conversation history (without the retrieved context to keep it clean)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": assistant_reply})

            # Print response
            print(f"Assistant: {assistant_reply}\n")
            print("-" * 70)
            print()

        except Exception as e:
            print(f"\n[ERROR] Failed to get response from Ollama: {e}")
            print("Make sure Ollama is running: ollama serve\n")


def main():
    print("=" * 70)
    print("  RAG-based Grade Discussion Chatbot")
    print(f"  LLM Model: {OLLAMA_MODEL}")
    print(f"  Embedding Model: {EMBEDDING_MODEL}")
    print("=" * 70)

    # Check if Ollama is available
    print("\n[Checking Ollama...]")
    try:
        models = ollama.list()
        available = [m.model for m in models.models]

        # Check LLM model
        if not any(OLLAMA_MODEL in m for m in available):
            print(f"\n[ERROR] Model '{OLLAMA_MODEL}' not found.")
            print(f"Please run: ollama pull {OLLAMA_MODEL}\n")
            return

        # Check embedding model
        if not any(EMBEDDING_MODEL in m for m in available):
            print(f"\n[WARNING] Embedding model '{EMBEDDING_MODEL}' not found.")
            print(f"Pulling it now... (this may take a moment)")
            ollama.pull(EMBEDDING_MODEL)

        print(f"  ✓ LLM Model '{OLLAMA_MODEL}' is ready")
        print(f"  ✓ Embedding Model '{EMBEDDING_MODEL}' is ready")

    except Exception as e:
        print(f"\n[ERROR] Cannot connect to Ollama: {e}")
        print("Please start Ollama: ollama serve\n")
        return

    # Ask for Moodle credentials
    print("\n" + "=" * 70)
    print("  Moodle Login")
    print("=" * 70)
    email = input("  Email   : ").strip()
    password = input("  Password: ").strip()

    if not email or not password:
        print("\n[ERROR] Email and password are required.")
        return

    # Log in via browser
    print("\n[Logging in to Moodle...] A browser window will open briefly.")
    try:
        session_cookie = get_session_cookie(email, password)
        print("  ✓ Login successful!\n")
    except RuntimeError as e:
        print(f"\n[ERROR] Login failed: {e}")
        return
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during login: {e}")
        return

    # Fetch grades
    try:
        client = MoodleClient(session_cookie)
        data = fetch_all_grades(client)

        student_name = data["profile"]["full_name"]

        # Create chunks for RAG
        chunks = create_grade_chunks(data)
        print(f"\n  ✓ Created {len(chunks)} information chunks for RAG")

        # Setup vector database
        collection = setup_vector_db(chunks)

        print("\n[RAG system ready!]")
        print("=" * 70)

        # Start RAG-based chat
        chat_loop(collection, student_name)

    except MoodleError as e:
        print(f"\n[ERROR] Moodle error: {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
