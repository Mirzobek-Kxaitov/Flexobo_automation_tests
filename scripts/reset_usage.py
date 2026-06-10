"""
Reset usage counters for all test users via admin panel.
Can be run standalone or imported as a helper.

Usage:
    python3 scripts/reset_usage.py              # Reset all users
    python3 scripts/reset_usage.py carrier       # Reset specific role
"""
import os
import sys
import re
from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv

load_dotenv()

ADMIN_URL = os.getenv("ADMIN_URL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Test user emails by role
TEST_USERS = {
    "broker": os.getenv("BROKER_EMAIL"),
    "load_owner": os.getenv("LOAD_OWNER_EMAIL"),
    "carrier": os.getenv("CARRIER_EMAIL"),
    "owner_operator": os.getenv("OWNER_OPERATOR_EMAIL"),
}


def admin_login(page: Page) -> None:
    """Log in to admin panel."""
    page.goto(f"{ADMIN_URL}/auth/sign-in")
    page.get_by_role("textbox", name="Email address").fill(ADMIN_EMAIL)
    page.get_by_role("textbox", name="Password").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_timeout(3000)


def reset_user_usage(page: Page, email: str) -> None:
    """Search a user by email and reset their usage counters."""
    search_box = page.get_by_role("textbox", name="Search by user ID")
    search_box.click()
    search_box.fill(email)
    page.wait_for_timeout(2000)

    row = page.get_by_role("row").filter(has_text=email)
    row.get_by_role("button").click()
    page.wait_for_timeout(500)

    page.get_by_role("menuitem", name="Reset usage").click()
    page.wait_for_timeout(500)

    page.get_by_role("button", name="Reset").click()
    page.wait_for_timeout(2000)


def reset_all_users(roles: list[str] | None = None) -> None:
    """Reset usage for specified roles (or all if None)."""
    targets = {r: TEST_USERS[r] for r in (roles or TEST_USERS)}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(30000)

        admin_login(page)

        page.get_by_role("link", name="User subscriptions").click()
        page.wait_for_timeout(2000)

        for role, email in targets.items():
            masked = email[0] + "***@" + email.split("@")[-1] if email else "???"
            print(f"Resetting {role} ({masked})...")
            reset_user_usage(page, email)
            print(f"  Done.")

        browser.close()

    print(f"\nAll {len(targets)} user(s) reset successfully.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        roles = [r.lower() for r in sys.argv[1:]]
        invalid = [r for r in roles if r not in TEST_USERS]
        if invalid:
            print(f"Unknown role(s): {invalid}")
            print(f"Available: {list(TEST_USERS.keys())}")
            sys.exit(1)
        reset_all_users(roles)
    else:
        reset_all_users()
