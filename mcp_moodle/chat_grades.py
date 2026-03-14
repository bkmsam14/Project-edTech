"""
Grade Discussion Chatbot with Ollama
-------------------------------------
Simple chatbot that:
  1. Asks for email/password
  2. Logs into Moodle via browser automation
  3. Fetches all your grades
  4. Lets you discuss your grades with an LLM (qwen2.5:3b)

Requirements:
  - Ollama installed and running (https://ollama.com/download)
  - Model pulled: ollama pull qwen2.5:3b
"""

import sys
import ollama
from moodle_login import get_session_cookie
from moodle_client import MoodleClient, MoodleError

OLLAMA_MODEL = "qwen2.5:3b"


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


def format_grades_for_llm(data: dict) -> str:
    """Format grade data as a readable text for the LLM context."""
    lines = []

    # Profile
    profile = data["profile"]
    lines.append("=== STUDENT PROFILE ===")
    lines.append(f"Name: {profile['full_name']}")
    lines.append(f"Email: {profile['email']}")
    lines.append("")

    # Grades
    lines.append("=== GRADES BY COURSE ===")
    lines.append("")

    for grade_info in data["grades"]:
        course_name = grade_info["course_name"]
        overall = grade_info["overall_grade"]
        items = grade_info["items"]

        lines.append(f"Course: {course_name}")
        lines.append(f"Overall Grade: {overall}")
        lines.append("Grade Items:")

        if items:
            for item in items:
                grade_display = item["grade"]
                if item["percentage"]:
                    grade_display += f" ({item['percentage']})"
                lines.append(f"  • {item['item']}: {grade_display}")
        else:
            lines.append("  (No detailed grades available)")

        lines.append("")

    return "\n".join(lines)


def chat_loop(grades_context: str):
    """Interactive chat loop with the LLM."""

    print("=" * 70)
    print("  Grade Discussion Chatbot Ready!")
    print("=" * 70)
    print("\nType your questions about your grades. Type 'quit' to exit.")
    print("\nExample questions:")
    print("  - What are my grades?")
    print("  - Which course am I doing best in?")
    print("  - What should I focus on improving?")
    print("  - Give me a summary of my performance")
    print("=" * 70)
    print()

    # Conversation history
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful academic advisor assistant. "
                "The student's grades are provided below. "
                "Answer questions about their academic performance, "
                "provide encouragement, and suggest areas for improvement.\n\n"
                f"{grades_context}"
            ),
        },
    ]

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

        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})

        print("\n[Thinking...]\n")

        # Get LLM response
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages,
            )

            assistant_reply = response.message.content

            # Add assistant reply to conversation history
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
    print("  Grade Discussion Chatbot")
    print(f"  Model: {OLLAMA_MODEL}")
    print("=" * 70)

    # Check if Ollama is available
    print("\n[Checking Ollama...]")
    try:
        models = ollama.list()
        available = [m.model for m in models.models]
        if not any(OLLAMA_MODEL in m for m in available):
            print(f"\n[ERROR] Model '{OLLAMA_MODEL}' not found.")
            print(f"Please run: ollama pull {OLLAMA_MODEL}\n")
            return
        else:
            print(f"  ✓ Model '{OLLAMA_MODEL}' is ready")
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

        # Format grades for LLM
        grades_context = format_grades_for_llm(data)

        print("\n[All grades loaded successfully!]")
        print("=" * 70)

        # Start chat
        chat_loop(grades_context)

    except MoodleError as e:
        print(f"\n[ERROR] Moodle error: {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
