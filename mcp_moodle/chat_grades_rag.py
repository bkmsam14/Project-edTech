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
import os
import tempfile
import ollama
import chromadb
from chromadb.utils import embedding_functions
from moodle_login import get_session_cookie
from moodle_client import MoodleClient, MoodleError
from file_parser import parse_file, chunk_text

OLLAMA_MODEL = "qwen2.5:3b"
EMBEDDING_MODEL = "nomic-embed-text"  # Ollama embedding model


def fetch_all_grades(client: MoodleClient) -> dict:
    """Fetch profile, courses, grades, quiz details, and course materials."""
    print("\n[Fetching your data from Moodle...]")

    # Get profile
    profile = client.get_site_info()
    print(f"  ✓ Profile: {profile['full_name']}")

    # Get all courses
    courses = client.get_enrolled_courses()
    print(f"  ✓ Found {len(courses)} course(s)")

    # Get grades for each course
    all_grades = []
    all_quizzes = []
    all_materials = []

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

            # Fetch quiz activities
            print(f"  ✓ Fetching quizzes for: {course['fullname']}")
            try:
                activities = client.get_course_activities(course["id"])
                quizzes = [a for a in activities if a["type"] == "quiz"]

                for quiz in quizzes:
                    print(f"    ↳ Found quiz: {quiz['name']}")
                    # Get quiz attempts
                    attempts = client.get_quiz_attempts(quiz["id"])

                    quiz_details = []
                    for attempt in attempts:
                        if attempt["attempt_id"]:
                            print(f"      → Reviewing attempt {attempt['attempt_number']}")
                            review = client.get_quiz_review(attempt["attempt_id"])
                            quiz_details.append({
                                "attempt_number": attempt["attempt_number"],
                                "grade": attempt["grade"],
                                "review": review,
                            })

                    if quiz_details:
                        all_quizzes.append({
                            "course_id": course["id"],
                            "course_name": course["fullname"],
                            "quiz_name": quiz["name"],
                            "quiz_id": quiz["id"],
                            "attempts": quiz_details,
                        })
            except Exception as e:
                print(f"    ⚠ Could not fetch quizzes: {e}")

            # Fetch course materials
            print(f"  ✓ Fetching materials for: {course['fullname']}")
            try:
                materials = client.get_course_materials(course["id"])

                for material in materials:
                    print(f"    ↳ Found {material['type']}: {material['name']}")

                    material_data = {
                        "course_id": course["id"],
                        "course_name": course["fullname"],
                        "material_type": material["type"],
                        "material_name": material["name"],
                        "material_id": material["id"],
                        "content": "",
                    }

                    # Extract content based on type
                    try:
                        if material["type"] == "page":
                            # Get HTML page content
                            page_data = client.get_page_content(material["id"])
                            material_data["content"] = f"{page_data['title']}\n\n{page_data['content']}"
                            print(f"      → Extracted page content ({len(material_data['content'])} chars)")

                        elif material["type"] == "resource":
                            # Download and parse file
                            temp_dir = tempfile.gettempdir()
                            file_ext = {
                                "pdf": ".pdf",
                                "docx": ".docx",
                                "pptx": ".pptx",
                            }.get(material.get("file_type", "unknown"), ".file")

                            temp_file = os.path.join(temp_dir, f"moodle_resource_{material['id']}{file_ext}")

                            try:
                                client.download_resource(material["id"], temp_file)
                                content = parse_file(temp_file, material.get("file_type"))
                                material_data["content"] = content
                                print(f"      → Parsed {material.get('file_type', 'file')} ({len(content)} chars)")

                                # Clean up temp file
                                if os.path.exists(temp_file):
                                    os.remove(temp_file)
                            except Exception as e:
                                print(f"      ⚠ Could not download/parse file: {e}")

                        elif material["type"] == "folder":
                            # Get files from folder
                            folder_files = client.get_folder_files(material["id"])
                            print(f"      → Found {len(folder_files)} files in folder")

                            # For now, just record folder contents
                            folder_content = f"Folder: {material['name']}\nContains:\n"
                            for file in folder_files:
                                folder_content += f"- {file['name']}\n"
                            material_data["content"] = folder_content

                    except Exception as e:
                        print(f"      ⚠ Error extracting content: {e}")

                    if material_data["content"]:
                        all_materials.append(material_data)

            except Exception as e:
                print(f"    ⚠ Could not fetch materials: {e}")

    return {
        "profile": profile,
        "courses": courses,
        "grades": all_grades,
        "quizzes": all_quizzes,
        "materials": all_materials,
    }


def create_grade_chunks(data: dict) -> list[dict]:
    """
    Create chunks of grade information for vector embedding.
    Each chunk is a logical piece of information (course overview, individual grades, quiz details, etc.)
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

    # Quiz chunks with detailed questions and answers
    for quiz_idx, quiz_info in enumerate(data.get("quizzes", [])):
        course_name = quiz_info["course_name"]
        quiz_name = quiz_info["quiz_name"]
        quiz_id = quiz_info["quiz_id"]

        for attempt in quiz_info["attempts"]:
            attempt_num = attempt["attempt_number"]
            attempt_grade = attempt["grade"]
            review = attempt["review"]

            # Quiz attempt overview chunk
            overview_text = (
                f"Course: {course_name}\n"
                f"Quiz: {quiz_name}\n"
                f"Attempt: {attempt_num}\n"
                f"Grade: {attempt_grade}\n"
                f"Overall Grade: {review.get('overall_grade', 'N/A')}"
            )

            chunks.append({
                "id": f"quiz_{quiz_id}_attempt_{attempt_num}_overview",
                "text": overview_text,
                "metadata": {
                    "type": "quiz_overview",
                    "course_name": course_name,
                    "quiz_name": quiz_name,
                    "attempt_number": attempt_num,
                },
            })

            # Individual question chunks
            for question in review.get("questions", []):
                q_num = question["question_number"]
                q_text = question["question_text"]
                student_ans = question["student_answer"]
                correct_ans = question["correct_answer"]
                outcome = question["outcome"]
                feedback = question["feedback"]
                q_grade = question["grade"]

                question_text = (
                    f"Course: {course_name}\n"
                    f"Quiz: {quiz_name} (Attempt {attempt_num})\n"
                    f"Question {q_num}: {q_text}\n"
                    f"Your Answer: {student_ans}\n"
                    f"Correct Answer: {correct_ans}\n"
                    f"Result: {outcome}\n"
                    f"Grade: {q_grade}\n"
                )

                if feedback:
                    question_text += f"Feedback: {feedback}\n"

                chunks.append({
                    "id": f"quiz_{quiz_id}_attempt_{attempt_num}_q{q_num}",
                    "text": question_text,
                    "metadata": {
                        "type": "quiz_question",
                        "course_name": course_name,
                        "quiz_name": quiz_name,
                        "attempt_number": attempt_num,
                        "question_number": q_num,
                        "outcome": outcome,
                    },
                })

            # Incorrect answers summary chunk
            incorrect_questions = [
                q for q in review.get("questions", [])
                if q["outcome"] in ["incorrect", "partially correct"]
            ]

            if incorrect_questions:
                mistakes_text = (
                    f"Course: {course_name}\n"
                    f"Quiz: {quiz_name} (Attempt {attempt_num})\n"
                    f"Mistakes Made:\n\n"
                )

                for q in incorrect_questions:
                    mistakes_text += (
                        f"Question {q['question_number']}: {q['question_text']}\n"
                        f"  Your Answer: {q['student_answer']}\n"
                        f"  Correct Answer: {q['correct_answer']}\n"
                        f"  Result: {q['outcome']}\n"
                    )
                    if q['feedback']:
                        mistakes_text += f"  Feedback: {q['feedback']}\n"
                    mistakes_text += "\n"

                chunks.append({
                    "id": f"quiz_{quiz_id}_attempt_{attempt_num}_mistakes",
                    "text": mistakes_text,
                    "metadata": {
                        "type": "quiz_mistakes",
                        "course_name": course_name,
                        "quiz_name": quiz_name,
                        "attempt_number": attempt_num,
                    },
                })

    # Course material chunks
    for mat_idx, material in enumerate(data.get("materials", [])):
        course_name = material["course_name"]
        material_type = material["material_type"]
        material_name = material["material_name"]
        material_id = material["material_id"]
        content = material["content"]

        if not content or len(content.strip()) < 50:
            continue  # Skip empty or very short content

        # Chunk the material content for better retrieval
        text_chunks = chunk_text(content, chunk_size=1500, overlap=300)

        for chunk_idx, chunk in enumerate(text_chunks):
            chunk_text_content = (
                f"Course: {course_name}\n"
                f"Material: {material_name} ({material_type})\n\n"
                f"{chunk}"
            )

            chunks.append({
                "id": f"material_{material_id}_chunk_{chunk_idx}",
                "text": chunk_text_content,
                "metadata": {
                    "type": "course_material",
                    "course_name": course_name,
                    "material_type": material_type,
                    "material_name": material_name,
                    "material_id": material_id,
                    "chunk_index": chunk_idx,
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
    print("  - What went wrong in [quiz name]?")
    print("  - Which quiz questions did I get wrong?")
    print("  - Show me my mistakes in the last quiz")
    print("  - What topics are covered in [lecture/material name]?")
    print("  - Explain [concept] from the course materials")
    print("  - What did we learn about [topic]?")
    print("  - Help me prepare for the quiz on [topic]")
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
                    "Answer questions about their academic performance based on the provided information. "
                    "You have access to:\n"
                    "- Course grades and assignments\n"
                    "- Quiz attempts with detailed questions, answers, and feedback\n"
                    "- Information about what went right and wrong in each quiz\n"
                    "- Course materials (lectures, PDFs, presentations, documents)\n"
                    "- Content from course pages and resources\n\n"
                    "When discussing quiz mistakes, be specific about:\n"
                    "- Which questions were answered incorrectly\n"
                    "- What the student answered vs the correct answer\n"
                    "- Any feedback or explanations provided\n\n"
                    "When discussing course materials:\n"
                    "- Reference specific topics and concepts from the materials\n"
                    "- Help connect what was taught to quiz questions\n"
                    "- Suggest relevant materials for review based on performance\n\n"
                    "Provide encouragement and suggest areas for improvement.\n\n"
                    "RELEVANT INFORMATION:\n"
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
