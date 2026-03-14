"""
Test script for Moodle login functionality.
This will open a browser, log in, and print the session cookie.
"""

from moodle_login import get_session_cookie

def main():
    print("=" * 60)
    print("  Moodle Login Test")
    print("=" * 60)

    # Get credentials from user
    email = input("Enter your Moodle email: ").strip()
    password = input("Enter your Moodle password: ").strip()

    if not email or not password:
        print("\n[ERROR] Email and password cannot be empty.")
        return

    print("\n[INFO] Starting login process...")
    print("[INFO] A browser window will open. Complete any MFA if required.\n")

    try:
        # Attempt login
        session_cookie = get_session_cookie(email, password)

        print("\n" + "=" * 60)
        print("✓ Login successful!")
        print("=" * 60)
        print(f"\nSession Cookie: {session_cookie}")
        print(f"\nCookie length: {len(session_cookie)} characters")
        print("\nYou can use this cookie to authenticate Moodle API calls.")
        print("=" * 60)

    except RuntimeError as e:
        print("\n" + "=" * 60)
        print("✗ Login failed!")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nPossible issues:")
        print("  - Wrong email or password")
        print("  - MFA timeout (you have 60 seconds to approve)")
        print("  - Network connection issue")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Unexpected error!")
        print("=" * 60)
        print(f"\nError: {e}")
        print("=" * 60)


if __name__ == "__main__":
    main()
