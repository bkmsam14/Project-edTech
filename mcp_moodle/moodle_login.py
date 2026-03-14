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

            # ── Step 2: if we're now on Microsoft login, handle it ─────────
            for _ in range(10):  # retry in case of multi-step MS login
                current = page.url

                # Microsoft email input step
                if "microsoftonline.com" in current or "microsoft.com" in current:
                    if page.locator("input[type='email']").is_visible():
                        print("[Browser] Entering Microsoft email...")
                        page.fill("input[type='email']", email)
                        page.click("input[type='submit'], #idSIButton9, button[type='submit']")
                        page.wait_for_load_state("domcontentloaded")
                        continue

                    # Microsoft password input step
                    if page.locator("input[type='password']").is_visible():
                        print("[Browser] Entering Microsoft password...")
                        page.fill("input[type='password']", password)
                        page.click("input[type='submit'], #idSIButton9, button[type='submit']")
                        page.wait_for_load_state("domcontentloaded")
                        continue

                    # "Stay signed in?" prompt
                    if page.locator("#idSIButton9").is_visible():
                        page.click("#idSIButton9")
                        page.wait_for_load_state("domcontentloaded")
                        continue

                # SSO button on Moodle page (some Moodle setups)
                sso_btn = page.locator("a:has-text('Microsoft'), a:has-text('Office'), "
                                       "a:has-text('Office 365'), a[href*='oidc'], "
                                       "a[href*='microsoft']")
                if sso_btn.count() > 0:
                    print("[Browser] Clicking SSO button...")
                    sso_btn.first.click()
                    page.wait_for_load_state("domcontentloaded")
                    continue

                # If we're back on Moodle (not login page) → done
                if MOODLE_URL in current and "/login" not in current:
                    break

                # If still on login with error → wrong credentials
                if "/login" in current and page.locator(".loginerrors, .alert-danger").count() > 0:
                    raise RuntimeError("Login failed: wrong email or password.")

                break  # no more steps to handle

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
