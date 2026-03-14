"""
Playwright-based Moodle login.
Handles both standard form and Microsoft Office 365 SSO automatically.
Opens a visible browser window so the user can complete MFA if needed.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

MOODLE_URL = "https://moodle.medtech.tn"


def get_session_cookie(email: str, password: str) -> str:
    """
    Logs into Moodle using the provided email and password.
    Handles both the standard Moodle form AND Microsoft SSO redirect.
    Returns the MoodleSession cookie value.
    Raises RuntimeError if login fails or times out.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page    = context.new_page()

        try:
            print("[Browser] Opening Moodle login page...")
            page.goto(f"{MOODLE_URL}/login/index.php", wait_until="domcontentloaded")

            # ── Step 1: fill standard Moodle form if present ──────────────
            if page.locator("#username").is_visible():
                print("[Browser] Filling standard login form...")
                page.fill("#username", email)
                page.fill("#password", password)
                page.click("#loginbtn")
                page.wait_for_load_state("domcontentloaded")

            

            # ── Step 3: wait until Moodle dashboard loads ─────────────────
            print("[Browser] Waiting for Moodle to load...")
            try:
                page.wait_for_url(
                    lambda url: MOODLE_URL in url and "/login" not in url,
                    timeout=60_000,  # 60 seconds — allows time for MFA
                )
            except PWTimeout:
                raise RuntimeError(
                    "Timed out waiting for login to complete.\n"
                    "If MFA is required, please approve it in the browser window."
                )

            # ── Step 4: extract MoodleSession cookie ──────────────────────
            cookies = context.cookies(MOODLE_URL)
            for c in cookies:
                if c["name"] == "MoodleSession":
                    print(f"[Browser] Session cookie obtained.")
                    return c["value"]

            raise RuntimeError("Logged in but MoodleSession cookie not found.")

        finally:
            browser.close()
