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


    def get_course_content(self, course_id: int) -> dict:
        """
        Scrape the course main page for section titles, activity names,
        and inline text content (Page resources, labels).

        Returns:
            {
              "course_id": int,
              "course_name": str,
              "sections": [
                {
                  "section_title": str,
                  "activities": [
                    {"name": str, "type": str, "content": str, "url": str}
                  ]
                }
              ]
            }
        """
        soup = self._get("/course/view.php", id=course_id)

        course_name = ""
        heading = soup.find("h1")
        if heading:
            course_name = heading.get_text(strip=True)

        sections = []
        # Moodle wraps each section in <li class="section"> or <div class="section">
        section_els = soup.select("li.section, div.section")

        for sec_el in section_els:
            # Section title
            title_el = sec_el.select_one(".sectionname, .section-title")
            section_title = title_el.get_text(strip=True) if title_el else ""

            activities = []

            # Activities are in <li class="activity"> elements
            for act_el in sec_el.select("li.activity, div.activity"):
                act_name_el = act_el.select_one(".activityname, .aalink, .instancename")
                act_name = act_name_el.get_text(strip=True) if act_name_el else ""

                # Determine type from CSS classes
                act_classes = " ".join(act_el.get("class", []))
                act_type = "unknown"
                for t in ("resource", "page", "url", "label", "folder",
                          "forum", "assign", "quiz", "book"):
                    if t in act_classes:
                        act_type = t
                        break

                # Get link
                link_el = act_el.find("a")
                act_url = link_el.get("href", "") if link_el else ""

                # Inline content (labels, summaries)
                content_el = act_el.select_one(".contentafterlink, .no-overflow, .label .mod-indent-outer")
                inline_content = content_el.get_text(" ", strip=True) if content_el else ""

                activities.append({
                    "name": act_name,
                    "type": act_type,
                    "content": inline_content,
                    "url": act_url,
                })

            if section_title or activities:
                sections.append({
                    "section_title": section_title,
                    "activities": activities,
                })

        return {
            "course_id": course_id,
            "course_name": course_name,
            "sections": sections,
        }

    def get_page_content(self, page_url: str) -> str:
        """
        Fetch and extract text from a Moodle 'Page' resource.

        Args:
            page_url: Full URL to the Moodle page resource.

        Returns:
            Extracted text content.
        """
        # Extract path from full URL
        path = page_url.replace(BASE_URL, "")
        if not path.startswith("/"):
            path = "/" + path
        soup = self._get(path)

        # Main content area
        content_el = soup.select_one("#region-main .no-overflow, #region-main .content, .generalbox")
        if content_el:
            return content_el.get_text(" ", strip=True)

        return ""


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
