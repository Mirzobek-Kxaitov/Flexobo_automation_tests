"""
Allure plugin — screenshot on failure, environment info, failure categories.

Pytest buni avtomatik yuklaydi (pytest.ini dagi -p plugins.allure_plugin orqali).
"""

import json
import os
import platform
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page


# ──────────────────────────────────────────────
# 1. Screenshot on failure
# ──────────────────────────────────────────────

# Page yetkazib beradigan barcha fixture'lar — multi-user testlarda har biridan
# alohida screenshot olinadi.
PAGE_FIXTURES = (
    "logged_in",
    "logged_in_broker",
    "logged_in_load_owner",
    "logged_in_carrier",
    "logged_in_owner_operator",
    "open_page",
    "landing_page",
)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Test fail bo'lsa, har bir page-fixture'dan screenshot oladi va Allure'ga attach qiladi."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    for fixture_name in PAGE_FIXTURES:
        page: Page | None = item.funcargs.get(fixture_name)
        if not page or page.is_closed():
            continue
        try:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"{item.name}__{fixture_name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass


# ──────────────────────────────────────────────
# 2. Environment & Categories (session tugaganda)
# ──────────────────────────────────────────────

def pytest_sessionfinish(session, exitstatus):
    """Allure-results papkasiga environment.properties va categories.json yozadi."""
    allure_dir = Path(session.config.option.allure_report_dir or "allure-results")
    allure_dir.mkdir(parents=True, exist_ok=True)

    # — environment.properties —
    env_data = {
        "Base URL": os.getenv("BASE_URL", ""),
        "Browser": "Chromium (Playwright)",
        "Python": platform.python_version(),
        "OS": os.name,
    }
    env_file = allure_dir / "environment.properties"
    env_file.write_text("\n".join(f"{k}={v}" for k, v in env_data.items()))

    # — categories.json —
    categories = [
        {
            "name": "Element topilmadi",
            "matchedStatuses": ["broken"],
            "messageRegex": ".*TimeoutError.*",
        },
        {
            "name": "Assertion xatosi",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*",
        },
        {
            "name": "Test muvaffaqiyatsiz",
            "matchedStatuses": ["failed"],
        },
    ]
    cat_file = allure_dir / "categories.json"
    cat_file.write_text(json.dumps(categories, indent=2, ensure_ascii=False))