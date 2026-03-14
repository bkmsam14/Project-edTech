"""
Moodle scraper — uses browser session cookie instead of API token.
Works with Office 365 / SSO accounts.

How to get your session cookie:
1. Log in to Moodle in your browser (via Office 365)
2. Press F12 → Application tab → Cookies → https://moodle.medtech.tn
3. Copy the value of the cookie named: MoodleSession
"""

import os
import re
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urljoin, unquote

load_dotenv()

BASE_URL = os.getenv("MOODLE_URL", "https://moodle.medtech.tn").rstrip("/")


class MoodleError(Exception):
    pass


class MoodleClient:
    def __init__(self, token: str = ""):
        """
        token: the value of the MoodleSession browser cookie.
        """
        self._session_cookie = token or os.getenv("MOODLE_TOKEN", "")
        self._userid: int | None = None
        self._username: str = ""

        if not self._session_cookie:
            raise MoodleError(
                "No session cookie provided.\n"
                "  1. Log in to Moodle in your browser (via Office 365)\n"
                "  2. Press F12 → Application → Cookies → moodle.medtech.tn\n"
                "  3. Copy the value of 'MoodleSession'"
            )

    # ── HTTP helper ───────────────────────────────────────────────────────────

    def _get(self, path: str, **params) -> BeautifulSoup:
        """Authenticated GET request, returns parsed HTML."""
        resp = httpx.get(
            f"{BASE_URL}{path}",
            params=params,
            cookies={"MoodleSession": self._session_cookie},
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
            timeout=20,
        )
        resp.raise_for_status()

        # If redirected to login page, session is expired or invalid
        if "/login/index.php" in str(resp.url):
            raise MoodleError(
                "Session cookie is invalid or expired.\n"
                "Please get a fresh MoodleSession cookie from your browser."
            )

        return BeautifulSoup(resp.text, "html.parser")

    # ── Public methods ────────────────────────────────────────────────────────

    def get_site_info(self) -> dict:
        """Return the logged-in user's profile information."""
        soup = self._get("/user/profile.php")

        full_name = ""
        h1 = soup.find("h1")
        if h1:
            full_name = h1.get_text(strip=True)

        email = ""
        for row in soup.select("dl.list dt"):
            if "email" in row.get_text(strip=True).lower():
                sibling = row.find_next_sibling("dd")
                if sibling:
                    email = sibling.get_text(strip=True)
                    break

        # Try to get user ID from the page URL or a form input
        userid = None
        id_input = soup.find("input", {"name": "id"})
        if id_input:
            userid = id_input.get("value")

        self._username = full_name
        return {
            "full_name":  full_name,
            "email":      email,
            "user_id":    userid,
            "site_name":  "MedTech Moodle",
            "site_url":   BASE_URL,
        }

    def get_enrolled_courses(self) -> list[dict]:
        """Return all courses from the grade overview page."""
        soup = self._get("/grade/report/overview/index.php")

        courses = []
        table = soup.find("table")
        if not table:
            return courses

        for row in table.select("tbody tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            # First cell: course name with link
            link = cells[0].find("a")
            if not link:
                continue

            course_name = link.get_text(strip=True)
            href        = link.get("href", "")

            # Extract course ID from href like /course/view.php?id=42
            m = re.search(r"[?&]id=(\d+)", href)
            course_id = int(m.group(1)) if m else None

            # Last cell: overall grade
            grade = cells[-1].get_text(strip=True)

            courses.append({
                "id":        course_id,
                "fullname":  course_name,
                "shortname": course_name,
                "category":  None,
                "progress":  None,
                "grade":     grade,
            })

        return courses

    def get_grades(self, course_id: int) -> dict:
        """Return detailed grade items for a specific course."""
        soup       = self._get("/grade/report/user/index.php", id=course_id)
        course_name = ""

        # Try to find the course name in the page heading
        heading = soup.find("h1") or soup.find("h2")
        if heading:
            course_name = heading.get_text(strip=True)

        items = []
        table = soup.find("table", class_=re.compile(r"user-grade|generaltable"))
        if not table:
            return {"course_id": course_id, "course_name": course_name, "items": items}

        for row in table.select("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            item_name = cells[0].get_text(" ", strip=True)
            # Skip header rows
            if not item_name or item_name.lower() in ("grade item", "grade", "name"):
                continue

            # Grade value is usually the 2nd or 3rd cell
            grade_val = ""
            for cell in cells[1:]:
                text = cell.get_text(strip=True)
                if text and text != "-":
                    grade_val = text
                    break

            # Percentage (look for a cell with %)
            pct = ""
            for cell in cells[1:]:
                text = cell.get_text(strip=True)
                if "%" in text:
                    pct = text
                    break

            items.append({
                "item":       item_name,
                "grade":      grade_val,
                "percentage": pct,
                "feedback":   "",
            })

        return {
            "course_id":   course_id,
            "course_name": course_name,
            "items":       items,
        }

    def get_course_activities(self, course_id: int) -> list[dict]:
        """Get all activities (including quizzes) from a course."""
        soup = self._get("/course/view.php", id=course_id)

        activities = []
        # Look for quiz links
        for link in soup.find_all("a", href=re.compile(r"/mod/quiz/view\.php\?id=\d+")):
            href = link.get("href", "")
            m = re.search(r"id=(\d+)", href)
            if m:
                activity_id = int(m.group(1))
                activity_name = link.get_text(strip=True)
                activities.append({
                    "type": "quiz",
                    "id": activity_id,
                    "name": activity_name,
                })

        return activities

    def get_quiz_attempts(self, quiz_id: int) -> list[dict]:
        """Get all attempts for a specific quiz."""
        soup = self._get("/mod/quiz/view.php", id=quiz_id)

        attempts = []
        # Find the attempts table
        table = soup.find("table", class_=re.compile(r"quizattemptsummary|generaltable"))

        if not table:
            return attempts

        for row in table.select("tbody tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue

            # Extract attempt number
            attempt_num_text = cells[0].get_text(strip=True)
            attempt_num = None
            m = re.search(r"\d+", attempt_num_text)
            if m:
                attempt_num = int(m.group(0))

            # Extract grade
            grade_text = ""
            for cell in cells:
                text = cell.get_text(strip=True)
                if "/" in text or "%" in text:
                    grade_text = text
                    break

            # Look for review link
            review_link = row.find("a", href=re.compile(r"/mod/quiz/review\.php"))
            attempt_id = None
            if review_link:
                href = review_link.get("href", "")
                m = re.search(r"attempt=(\d+)", href)
                if m:
                    attempt_id = int(m.group(1))

            if attempt_num is not None:
                attempts.append({
                    "attempt_number": attempt_num,
                    "attempt_id": attempt_id,
                    "grade": grade_text,
                })

        return attempts

    def get_quiz_review(self, attempt_id: int) -> dict:
        """Get detailed review of a quiz attempt including questions and answers."""
        soup = self._get("/mod/quiz/review.php", attempt=attempt_id)

        # Get quiz name
        quiz_name = ""
        h2 = soup.find("h2")
        if h2:
            quiz_name = h2.get_text(strip=True)

        # Get overall grade
        grade_info = ""
        grade_elem = soup.find(class_=re.compile(r"grade"))
        if grade_elem:
            grade_info = grade_elem.get_text(strip=True)

        # Extract questions
        questions = []
        question_divs = soup.find_all("div", class_=re.compile(r"que\s"))

        for idx, q_div in enumerate(question_divs, 1):
            # Question text
            q_text_elem = q_div.find(class_=re.compile(r"qtext"))
            q_text = q_text_elem.get_text(" ", strip=True) if q_text_elem else ""

            # Question type (multichoice, truefalse, etc)
            q_type = ""
            classes = q_div.get("class", [])
            for cls in classes:
                if cls.startswith("que"):
                    q_type = cls
                    break

            # Student's answer
            student_answer = ""
            answer_elem = q_div.find(class_=re.compile(r"answer"))
            if answer_elem:
                student_answer = answer_elem.get_text(" ", strip=True)

            # Correct answer / feedback
            correct_answer = ""
            rightanswer_elem = q_div.find(class_=re.compile(r"rightanswer"))
            if rightanswer_elem:
                correct_answer = rightanswer_elem.get_text(" ", strip=True)

            # Grade / result for this question
            q_grade = ""
            grade_elem = q_div.find(class_=re.compile(r"grade"))
            if grade_elem:
                q_grade = grade_elem.get_text(strip=True)

            # Outcome (correct/incorrect)
            outcome = "unknown"
            if "correct" in q_div.get("class", []):
                outcome = "correct"
            elif "incorrect" in q_div.get("class", []):
                outcome = "incorrect"
            elif "partiallycorrect" in q_div.get("class", []):
                outcome = "partially correct"

            # Feedback
            feedback = ""
            feedback_elem = q_div.find(class_=re.compile(r"feedback"))
            if feedback_elem:
                feedback = feedback_elem.get_text(" ", strip=True)

            questions.append({
                "question_number": idx,
                "question_text": q_text,
                "question_type": q_type,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "grade": q_grade,
                "outcome": outcome,
                "feedback": feedback,
            })

        return {
            "quiz_name": quiz_name,
            "overall_grade": grade_info,
            "questions": questions,
        }

    def get_course_materials(self, course_id: int) -> list[dict]:
        """Get all course materials (PDFs, docs, pages, etc.) from a course."""
        soup = self._get("/course/view.php", id=course_id)

        materials = []

        # Find resource links (PDF, DOC, PPT, etc.)
        for link in soup.find_all("a", href=re.compile(r"/mod/resource/view\.php\?id=\d+")):
            href = link.get("href", "")
            m = re.search(r"id=(\d+)", href)
            if m:
                resource_id = int(m.group(1))
                resource_name = link.get_text(strip=True)

                # Try to detect file type from icon or name
                file_type = "unknown"
                if ".pdf" in resource_name.lower() or "pdf" in str(link):
                    file_type = "pdf"
                elif ".doc" in resource_name.lower() or "word" in str(link):
                    file_type = "docx"
                elif ".ppt" in resource_name.lower() or "powerpoint" in str(link):
                    file_type = "pptx"

                materials.append({
                    "type": "resource",
                    "file_type": file_type,
                    "id": resource_id,
                    "name": resource_name,
                })

        # Find page content (HTML pages)
        for link in soup.find_all("a", href=re.compile(r"/mod/page/view\.php\?id=\d+")):
            href = link.get("href", "")
            m = re.search(r"id=(\d+)", href)
            if m:
                page_id = int(m.group(1))
                page_name = link.get_text(strip=True)
                materials.append({
                    "type": "page",
                    "id": page_id,
                    "name": page_name,
                })

        # Find folder links
        for link in soup.find_all("a", href=re.compile(r"/mod/folder/view\.php\?id=\d+")):
            href = link.get("href", "")
            m = re.search(r"id=(\d+)", href)
            if m:
                folder_id = int(m.group(1))
                folder_name = link.get_text(strip=True)
                materials.append({
                    "type": "folder",
                    "id": folder_id,
                    "name": folder_name,
                })

        return materials

    def get_page_content(self, page_id: int) -> dict:
        """Get content from a Moodle page."""
        soup = self._get("/mod/page/view.php", id=page_id)

        # Get page title
        title = ""
        h2 = soup.find("h2")
        if h2:
            title = h2.get_text(strip=True)

        # Get page content
        content = ""
        content_div = soup.find("div", class_=re.compile(r"page-content|content"))
        if content_div:
            # Get text content, preserving some structure
            content = content_div.get_text(" ", strip=True)

        return {
            "title": title,
            "content": content,
        }

    def download_resource(self, resource_id: int, save_path: str) -> str:
        """Download a file resource from Moodle."""
        # First, get the resource page to find the actual download link
        soup = self._get("/mod/resource/view.php", id=resource_id)

        # Find the download link
        download_link = None
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "/pluginfile.php/" in href or "forcedownload=1" in href:
                download_link = href
                break

        if not download_link:
            raise MoodleError(f"Could not find download link for resource {resource_id}")

        # Make the download link absolute
        if not download_link.startswith("http"):
            download_link = urljoin(BASE_URL, download_link)

        # Download the file
        resp = httpx.get(
            download_link,
            cookies={"MoodleSession": self._session_cookie},
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
            timeout=60,
        )
        resp.raise_for_status()

        # Save to file
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(resp.content)

        return save_path

    def get_folder_files(self, folder_id: int) -> list[dict]:
        """Get all files from a Moodle folder."""
        soup = self._get("/mod/folder/view.php", id=folder_id)

        files = []
        # Find all file links in the folder
        for link in soup.find_all("a", href=re.compile(r"/pluginfile\.php/")):
            href = link.get("href", "")
            file_name = link.get_text(strip=True) or unquote(href.split("/")[-1])

            # Detect file type
            file_type = "unknown"
            if file_name.lower().endswith(".pdf"):
                file_type = "pdf"
            elif file_name.lower().endswith((".doc", ".docx")):
                file_type = "docx"
            elif file_name.lower().endswith((".ppt", ".pptx")):
                file_type = "pptx"

            # Make link absolute
            if not href.startswith("http"):
                href = urljoin(BASE_URL, href)

            files.append({
                "name": file_name,
                "url": href,
                "file_type": file_type,
            })

        return files


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text or "").strip()


# ── Quick connection test ─────────────────────────────────────────────────────

if __name__ == "__main__":
    from moodle_login import get_session_cookie

    print("=" * 55)
    print("  Moodle connection test")
    print("=" * 55)
    email    = input("  Email   : ").strip()
    password = input("  Password: ").strip()

    print("\n[Logging in...] A browser window will open briefly.")
    try:
        session = get_session_cookie(email, password)
        print("[Login successful]\n")
    except RuntimeError as e:
        print(f"\n[ERROR] {e}")
        raise SystemExit(1)

    try:
        client = MoodleClient(session)

        print("[1/3] Fetching profile...")
        info = client.get_site_info()
        print(f"      Name  : {info['full_name']}")
        print(f"      Email : {info['email']}")

        print("\n[2/3] Fetching enrolled courses + grades overview...")
        courses = client.get_enrolled_courses()
        if courses:
            for c in courses:
                print(f"      [{c['id']}] {c['fullname']}  — {c.get('grade','')}")
        else:
            print("      No courses found.")

        print("\n[3/3] Fetching detailed grades for all courses...")
        if courses:
            for course in courses:
                if course["id"]:
                    print(f"\n      Course: {course['fullname']}")
                    print("      " + "=" * 50)
                    data  = client.get_grades(course["id"])
                    items = data.get("items", [])
                    if items:
                        for item in items:
                            grade_display = f"{item['grade']}"
                            if item['percentage']:
                                grade_display += f" ({item['percentage']})"
                            print(f"        • {item['item']}: {grade_display}")
                    else:
                        print("        No grade items found.")
        else:
            print("      No courses found.")

        print("\n[OK] Everything works!")

    except MoodleError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
