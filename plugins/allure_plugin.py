"""
Allure plugin — screenshot on failure, environment info, failure categories.

Pytest buni avtomatik yuklaydi (pytest.ini dagi -p plugins.allure_plugin orqali).
"""

import json
import os
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page


# ──────────────────────────────────────────────
# 1. Screenshot on failure
# ──────────────────────────────────────────────

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Test fail bo'lsa, Playwright page'dan screenshot oladi va Allure'ga attach qiladi."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Playwright fixture'dan page olish
        page: Page | None = item.funcargs.get("logged_in") or item.funcargs.get("open_page") or item.funcargs.get("landing_page")

        if page and not page.is_closed():
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"{item.name}_failure",
                attachment_type=allure.attachment_type.PNG,
            )


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
        "Python": f"{session.config._inicache.get('python', '')}",
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