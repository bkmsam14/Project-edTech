from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import uuid
import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


# ── helpers ───────────────────────────────────────────────────────────────────

def _supabase_available() -> bool:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_ANON_KEY", "") or os.getenv("SUPABASE_KEY", "")
    svc = os.getenv("SUPABASE_SERVICE_KEY", "")
    return bool(url and key and svc)


def _get_clients():
    from database import get_supabase_client, get_supabase_admin
    return get_supabase_client(), get_supabase_admin()

# ── request / response models ─────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
    age_group: Optional[str] = None
    grade_level: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    access_token: str
    refresh_token: Optional[str] = None
    user: dict


class MessageResponse(BaseModel):
    success: bool
    message: str


# ── signup ────────────────────────────────────────────────────────────────────

@router.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """
    Register a new user.
    Gracefully falls back to a local-only token if Supabase is not configured.
    """
    if not _supabase_available():
        local_id = f"local_{uuid.uuid4().hex[:12]}"
        return AuthResponse(
            success=True,
            access_token=f"local_token_{local_id}",
            user={
                "user_id": local_id,
                "email": request.email,
                "full_name": request.full_name,
                "onboarding_completed": False,
            }
        )

    try:
        supabase, admin = _get_clients()

        auth_resp = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })

        if not auth_resp.user:
            raise HTTPException(status_code=400, detail="Email may already be in use.")

        auth_user_id = auth_resp.user.id
        user_id = str(uuid.uuid4())

        admin.table("users").insert({
            "user_id": user_id,
            "auth_user_id": auth_user_id,
            "full_name": request.full_name,
            "email": request.email,
            "age_group": request.age_group,
            "grade_level": request.grade_level,
            "learning_level": "beginner",
            "onboarding_completed": False,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        admin.table("accessibility_settings").insert({
            "user_id": user_id,
            "font_size_px": 18,
            "line_height": 1.6,
            "tts_enabled": False,
        }).execute()

        admin.table("learning_preferences").insert({
            "user_id": user_id,
            "learning_style": "balanced",
            "quiz_frequency": "medium",
            "gamification_enabled": True,
        }).execute()

        logger.info(f"User created: {user_id}")

        return AuthResponse(
            success=True,
            access_token=auth_resp.session.access_token,
            refresh_token=auth_resp.session.refresh_token,
            user={
                "user_id": user_id,
                "email": request.email,
                "full_name": request.full_name,
                "onboarding_completed": False,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── login ─────────────────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate and return tokens."""
    if not _supabase_available():
        raise HTTPException(
            status_code=503,
            detail="Auth service not configured. Set SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_KEY."
        )

    try:
        supabase, admin = _get_clients()

        auth_resp = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if not auth_resp.user:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        result = admin.table("users").select("*").eq("auth_user_id", auth_resp.user.id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="User profile not found.")

        user = result.data

        try:
            admin.table("users").update({"last_login_at": datetime.utcnow().isoformat()}).eq("user_id", user["user_id"]).execute()
        except Exception:
            pass

        logger.info(f"User logged in: {user['user_id']}")

        return AuthResponse(
            success=True,
            access_token=auth_resp.session.access_token,
            refresh_token=auth_resp.session.refresh_token,
            user={
                "user_id": user["user_id"],
                "email": user["email"],
                "full_name": user.get("full_name", ""),
                "onboarding_completed": user.get("onboarding_completed", False),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── logout ────────────────────────────────────────────────────────────────────

@router.post("/auth/logout", response_model=MessageResponse)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if _supabase_available() and credentials:
        try:
            supabase, _ = _get_clients()
            supabase.auth.sign_out()
        except Exception:
            pass
    return MessageResponse(success=True, message="Logged out successfully.")


# ── current user ──────────────────────────────────────────────────────────────

@router.get("/auth/me")
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    if not _supabase_available():
        raise HTTPException(status_code=503, detail="Auth service not configured.")

    try:
        supabase, admin = _get_clients()
        user_resp = supabase.auth.get_user(credentials.credentials)

        if not user_resp or not user_resp.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token.")

        result = admin.table("users").select("*").eq("auth_user_id", user_resp.user.id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found.")

        return result.data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get me error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed.")


# ── shared dependency ─────────────────────────────────────────────────────────

async def get_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """
    Extracts user_id from Bearer token.
    Returns None when Supabase is not configured so other routes keep working
    with the user_id they receive in the request body.
    """
    if not credentials or not _supabase_available():
        return None
    try:
        supabase, admin = _get_clients()
        user_resp = supabase.auth.get_user(credentials.credentials)
        if not user_resp or not user_resp.user:
            return None
        result = admin.table("users").select("user_id").eq("auth_user_id", user_resp.user.id).single().execute()
        return result.data["user_id"] if result.data else None
    except Exception:
        return None
