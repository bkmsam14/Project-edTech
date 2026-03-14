"""
Run this to verify your Supabase connection is working.

    python test_connection.py
"""

import sys
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Check .env was loaded
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url or "your-project-id" in url:
    print("ERROR: SUPABASE_URL not set. Open .env and paste your Project URL.")
    sys.exit(1)

if not key or "your-anon-key" in key:
    print("ERROR: SUPABASE_ANON_KEY not set. Open .env and paste your anon key.")
    sys.exit(1)

print(f"URL loaded:  {url}")
print(f"Key loaded:  {key[:20]}...")

# 2. Try connecting
try:
    from supabase import create_client
    client = create_client(url, key)
    print("\nSupabase client created successfully.")
except Exception as e:
    print(f"\nERROR creating client: {e}")
    sys.exit(1)

# 3. Try a real query (will succeed even if tables don't exist yet)
try:
    result = client.table("users").select("user_id").limit(1).execute()
    print("Connection confirmed — query ran without errors.")
    print("You are ready to run the SQL files in Supabase.")
except Exception as e:
    err = str(e)
    if "does not exist" in err.lower() or "PGRST205" in err or "schema cache" in err.lower():
        print("Connection confirmed — tables not created yet (expected).")
        print("Next step: run the SQL files in your Supabase SQL editor.")
    else:
        print(f"Connection error: {e}")
        sys.exit(1)
