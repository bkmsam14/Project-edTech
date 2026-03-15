"""Moodle integration routes — connect, list courses, select course, grades"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import sys
import os

logger = logging.getLogger(__name__)

# Ensure src/ is on the path so mcp_moodle imports resolve
_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

_project_root = os.path.abspath(os.path.join(_src_dir, ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from mcp_moodle.moodle_client import MoodleClient, MoodleError

router = APIRouter(prefix="/moodle", tags=["Moodle"])

# In-memory stores
_moodle_sessions: Dict[str, MoodleClient] = {}
_moodle_courses: Dict[str, dict] = {}
_moodle_grades: Dict[str, dict] = {}


# ── Request / Response schemas ────────────────────────────────────────────

class MoodleConnectRequest(BaseModel):
    user_id: str
    session_cookie: str


class MoodleConnectResponse(BaseModel):
    success: bool
    profile: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CourseListResponse(BaseModel):
    success: bool
    courses: List[Dict[str, Any]] = []


class CourseSelectRequest(BaseModel):
    user_id: str
    course_id: int
    course_name: str


class CourseSelectResponse(BaseModel):
    success: bool
    course: Optional[Dict[str, Any]] = None
    grades: Optional[Dict[str, Any]] = None
    ingestion_stats: Optional[Dict[str, Any]] = None


class GradesResponse(BaseModel):
    success: bool
    grades: Optional[Dict[str, Any]] = None


class MoodleStatusResponse(BaseModel):
    success: bool
    connected: bool
    profile: Optional[Dict[str, Any]] = None
    selected_course: Optional[Dict[str, Any]] = None


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/connect", response_model=MoodleConnectResponse)
async def connect_moodle(request: MoodleConnectRequest):
    """Validate a MoodleSession cookie and store the connection."""
    try:
        client = MoodleClient(token=request.session_cookie)
        profile = client.get_site_info()

        _moodle_sessions[request.user_id] = client
        logger.info(f"Moodle connected for user {request.user_id}: {profile.get('full_name')}")

        return MoodleConnectResponse(success=True, profile=profile)

    except MoodleError as e:
        logger.warning(f"Moodle connection failed for {request.user_id}: {e}")
        return MoodleConnectResponse(success=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error connecting to Moodle: {e}")
        return MoodleConnectResponse(success=False, error=str(e))


@router.get("/courses/{user_id}", response_model=CourseListResponse)
async def list_courses(user_id: str):
    """List enrolled courses from Moodle."""
    client = _moodle_sessions.get(user_id)
    if not client:
        raise HTTPException(status_code=401, detail="Not connected to Moodle. Please connect first.")

    try:
        courses = client.get_enrolled_courses()
        return CourseListResponse(success=True, courses=courses)
    except MoodleError as e:
        raise HTTPException(status_code=401, detail=f"Moodle session expired: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select-course", response_model=CourseSelectResponse)
async def select_course(request: CourseSelectRequest):
    """Select a course, fetch grades, and ingest course content into the vector store."""
    client = _moodle_sessions.get(request.user_id)
    if not client:
        raise HTTPException(status_code=401, detail="Not connected to Moodle. Please connect first.")

    try:
        # Fetch grades
        grades = client.get_grades(request.course_id)

        # Store course selection
        course_info = {
            "course_id": request.course_id,
            "course_name": request.course_name,
            "document_id": f"moodle_course_{request.course_id}",
        }
        _moodle_courses[request.user_id] = course_info
        _moodle_grades[request.user_id] = grades

        # Ingest course content into ChromaDB
        ingestion_stats = None
        try:
            from mcp_moodle.ingest_moodle_content import ingest_course
            stats = ingest_course(client, request.course_id, request.course_name, tenant_id="default")
            ingestion_stats = stats
            logger.info(f"Ingested course {request.course_name}: {stats}")
        except Exception as e:
            logger.warning(f"Course ingestion failed (non-blocking): {e}")
            ingestion_stats = {"error": str(e)}

        return CourseSelectResponse(
            success=True,
            course=course_info,
            grades=grades,
            ingestion_stats=ingestion_stats,
        )

    except MoodleError as e:
        raise HTTPException(status_code=401, detail=f"Moodle session expired: {e}")
    except Exception as e:
        logger.error(f"Error selecting course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grades/{user_id}/{course_id}", response_model=GradesResponse)
async def get_grades(user_id: str, course_id: int):
    """Get detailed grades for a specific course."""
    client = _moodle_sessions.get(user_id)
    if not client:
        raise HTTPException(status_code=401, detail="Not connected to Moodle. Please connect first.")

    try:
        grades = client.get_grades(course_id)
        return GradesResponse(success=True, grades=grades)
    except MoodleError as e:
        raise HTTPException(status_code=401, detail=f"Moodle session expired: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{user_id}", response_model=MoodleStatusResponse)
async def moodle_status(user_id: str):
    """Check Moodle connection and course selection status."""
    client = _moodle_sessions.get(user_id)
    connected = client is not None
    selected_course = _moodle_courses.get(user_id)

    profile = None
    if connected:
        try:
            profile = client.get_site_info()
        except Exception:
            # Session may have expired
            connected = False

    return MoodleStatusResponse(
        success=True,
        connected=connected,
        profile=profile,
        selected_course=selected_course,
    )
