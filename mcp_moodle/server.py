import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from moodle_client import MoodleClient, MoodleError

# Create MCP server
mcp = FastMCP("Example MCP Server")


# Tool 1: Hello world
@mcp.tool()
def hello(name: str = "World") -> str:
    """Return a hello message for the given name."""
    return f"Hello, {name}! Greetings from MCP Server."


# Tool 2: Add two numbers
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


# Tool 3: Reverse a string
@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverse the given string."""
    return text[::-1]


# Tool 4: Get current date and time
@mcp.tool()
def get_current_date(timezone: str = "local") -> str:
    """
    Get the current date and time.
    Returns today's date, current time, day of the week, and more.
    Use this whenever the user asks about the current date or time.
    """
    now = datetime.now()
    return (
        f"Current date : {now.strftime('%A, %B %d, %Y')}\n"
        f"Current time : {now.strftime('%H:%M:%S')}\n"
        f"Day of week  : {now.strftime('%A')}\n"
        f"Day of year  : {now.strftime('%j')}\n"
        f"Week number  : {now.strftime('%W')}\n"
        f"Timezone     : {timezone} (system local)"
    )


# ── Moodle tools ──────────────────────────────────────────────────────────────

@mcp.tool()
def moodle_get_profile(token: str) -> str:
    """
    Retrieve the logged-in Moodle user's profile information.
    Returns name, username, email, and site details.
    Requires the user's Moodle personal API token.
    """
    try:
        client = MoodleClient(token)
        info   = client.get_site_info()
        return json.dumps(info, indent=2)
    except MoodleError as e:
        return f"Moodle error: {e}"
    except Exception as e:
        return f"Connection error: {e}"


@mcp.tool()
def moodle_get_courses(token: str) -> str:
    """
    Retrieve all courses the user is currently enrolled in on Moodle.
    Returns the course name, short name, category, and progress for each course.
    Requires the user's Moodle personal API token.
    """
    try:
        client  = MoodleClient(token)
        courses = client.get_enrolled_courses()
        if not courses:
            return "No enrolled courses found."
        lines = [f"Found {len(courses)} enrolled course(s):\n"]
        for c in courses:
            lines.append(f"  [{c['id']}] {c['fullname']}  ({c['shortname']})")
            if c.get("category"):
                lines.append(f"       Category : {c['category']}")
            if c.get("progress") is not None:
                lines.append(f"       Progress : {c['progress']}%")
        return "\n".join(lines)
    except MoodleError as e:
        return f"Moodle error: {e}"
    except Exception as e:
        return f"Connection error: {e}"


@mcp.tool()
def moodle_get_grades(token: str, course_id: int) -> str:
    """
    Retrieve the grades for the user in a specific Moodle course.
    Requires the user's Moodle personal API token and the numeric course ID
    (obtainable by calling moodle_get_courses first).
    Returns each grade item, the score, percentage, and feedback.
    """
    try:
        client = MoodleClient(token)
        data   = client.get_grades(course_id)
        items  = data.get("items", [])
        if not items:
            return f"No grade items found for course {course_id}."

        lines = [f"Grades for: {data.get('course_name', course_id)}\n"]
        for item in items:
            name  = item.get("item") or "Unnamed item"
            grade = item.get("grade", "-")
            pct   = item.get("percentage", "")
            fb    = item.get("feedback", "")
            line  = f"  {name}: {grade}"
            if pct:
                line += f"  ({pct})"
            lines.append(line)
            if fb:
                lines.append(f"    Feedback: {fb}")
        return "\n".join(lines)
    except MoodleError as e:
        return f"Moodle error: {e}"
    except Exception as e:
        return f"Connection error: {e}"


# ── Resource: A static info page
@mcp.resource("info://server")
def server_info() -> str:
    """Returns info about this MCP server."""
    return "MCP server tools: hello, add, reverse_string, get_current_date, moodle_get_profile, moodle_get_courses, moodle_get_grades."


# Run server
# Default transport is stdio (for subprocess-based clients)
# To run with SSE (HTTP), use: mcp.run(transport="sse")
if __name__ == "__main__":
    import sys

    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if transport == "sse":
        # HTTP/SSE mode — client connects over network
        mcp.run(transport="sse")
    else:
        # stdio mode — client spawns this as a subprocess
        mcp.run(transport="stdio")
