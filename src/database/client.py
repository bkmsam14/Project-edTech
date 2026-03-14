"""
Supabase client — single shared instance for the whole project.

Usage anywhere in the codebase:
    from src.database.client import supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_ANON_KEY"]

# Use SUPABASE_SERVICE_KEY for backend operations that need to bypass RLS
# (e.g. the Assessment Agent writing mastery scores)
SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", SUPABASE_KEY)

# Client for regular user-scoped operations (respects RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Client for backend/system operations (bypasses RLS)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
