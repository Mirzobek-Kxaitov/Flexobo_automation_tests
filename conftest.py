import os
import re
import sys
import json
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect, BrowserContext
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

# Legacy tests use EMAIL/PASSWORD — kept for backward compatibility
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

BASE_URL = os.getenv("BASE_URL")
APP_URL = os.getenv("APP_URL")

BROKER_EMAIL = os.getenv("BROKER_EMAIL")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")

LOAD_OWNER_EMAIL = os.getenv("LOAD_OWNER_EMAIL")
LOAD_OWNER_PASSWORD = os.getenv("LOAD_OWNER_PASSWORD")

CARRIER_EMAIL = os.getenv("CARRIER_EMAIL")
CARRIER_PASSWORD = os.getenv("CARRIER_PASSWORD")

OWNER_OPERATOR_EMAIL = os.getenv("OWNER_OPERATOR_EMAIL")
OWNER_OPERATOR_PASSWORD = os.getenv("OWNER_OPERATOR_PASSWORD")

# FREE plan users (for limit enforcement tests)
FREE_BROKER_EMAIL = os.getenv("FREE_BROKER_EMAIL")
FREE_BROKER_PASSWORD = os.getenv("FREE_BROKER_PASSWORD")
FREE_LOAD_OWNER_EMAIL = os.getenv("FREE_LOAD_OWNER_EMAIL")
FREE_LOAD_OWNER_PASSWORD = os.getenv("FREE_LOAD_OWNER_PASSWORD")
FREE_CARRIER_EMAIL = os.getenv("FREE_CARRIER_EMAIL")
FREE_CARRIER_PASSWORD = os.getenv("FREE_CARRIER_PASSWORD")
FREE_OWNER_OPERATOR_EMAIL = os.getenv("FREE_OWNER_OPERATOR_EMAIL")
FREE_OWNER_OPERATOR_PASSWORD = os.getenv("FREE_OWNER_OPERATOR_PASSWORD")

LOGIN_TIMEOUT_MS = int(os.getenv("LOGIN_TIMEOUT_MS", "60000"))

# Storage state cache directory
_STATE_DIR = Path(__file__).parent / ".auth"


def _required_env(name: str, value: str | None) -> str:
    if value:
        return value
    raise AssertionError(
        f"{name} is required but empty. Add it to local .env and GitHub repository secrets."
    )


def login_as(page: Page, email: str | None, password: str | None, label: str = "") -> Page:
    """Log in with the given email and password."""
    app_url = _required_env("APP_URL", APP_URL).rstrip("/")
    if not email or not password:
        raise AssertionError(
            f"{label} credentials are missing. Check local .env and GitHub repository secrets."
        )

    page.goto(f"{app_url}/sign-in?lang=en")
    page.get_by_test_id("login_email_input").fill(email)
    page.get_by_test_id("login_password_input").fill(password)
    page.get_by_test_id("login_submit_button").click()
    expect(page).not_to_have_url(re.compile(r".*sign-in.*"), timeout=LOGIN_TIMEOUT_MS)

    accept_button = page.get_by_test_id("global_cookie_accept_button")
    if accept_button.is_visible():
        accept_button.click(force=True)

    return page


def _get_storage_state(browser, browser_context_args, email, password, label) -> str:
    """Login once and cache storage_state to disk. Returns path to state file."""
    _STATE_DIR.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", label)
    state_path = _STATE_DIR / f"{safe_name}.json"

    if state_path.exists():
        return str(state_path)

    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    login_as(page, email, password, label)
    context.storage_state(path=str(state_path))
    context.close()
    return str(state_path)


def _context_from_state(browser, browser_context_args, state_path):
    """Create a new context using cached storage_state."""
    context = browser.new_context(storage_state=state_path, **browser_context_args)
    page = context.new_page()
    return context, page


def _logged_in_page(browser, browser_context_args, email, password, label):
    """Create a separate browser context with cached login session."""
    state_path = _get_storage_state(browser, browser_context_args, email, password, label)
    return _context_from_state(browser, browser_context_args, state_path)


@pytest.fixture(scope="session", autouse=True)
def _clean_auth_cache():
    """Clean auth cache at start/end of session — fresh login once per run."""
    import shutil
    if _STATE_DIR.exists():
        shutil.rmtree(_STATE_DIR)
    _STATE_DIR.mkdir(exist_ok=True)
    yield
    # Cleanup at end of session
    if _STATE_DIR.exists():
        shutil.rmtree(_STATE_DIR)


def pytest_addoption(parser):
    parser.addoption(
        "--reset-usage", action="store_true", default=False,
        help="Reset all test user usage counters via admin panel before tests",
    )


@pytest.fixture(scope="session", autouse=True)
def reset_usage_if_requested(request):
    """Reset all user usage counters when --reset-usage flag is passed."""
    if request.config.getoption("--reset-usage"):
        from reset_usage import reset_all_users
        reset_all_users()


@pytest.fixture
def open_page(page: Page):
    """Open the login page without performing a login."""
    page.goto(f"{_required_env('APP_URL', APP_URL).rstrip('/')}/sign-in?lang=en")
    return page


@pytest.fixture
def logged_in(browser, browser_context_args):
    """Log in as broker using the legacy EMAIL/PASSWORD credentials."""
    context, page = _logged_in_page(browser, browser_context_args, EMAIL, PASSWORD, "EMAIL/PASSWORD")
    yield page
    context.close()


@pytest.fixture
def logged_in_broker(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, BROKER_EMAIL, BROKER_PASSWORD, "BROKER_EMAIL/BROKER_PASSWORD"
    )
    yield page
    context.close()


@pytest.fixture
def logged_in_load_owner(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD,
        "LOAD_OWNER_EMAIL/LOAD_OWNER_PASSWORD",
    )
    yield page
    context.close()


@pytest.fixture
def logged_in_carrier(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, CARRIER_EMAIL, CARRIER_PASSWORD,
        "CARRIER_EMAIL/CARRIER_PASSWORD",
    )
    yield page
    context.close()


@pytest.fixture
def logged_in_owner_operator(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, OWNER_OPERATOR_EMAIL, OWNER_OPERATOR_PASSWORD,
        "OWNER_OPERATOR_EMAIL/OWNER_OPERATOR_PASSWORD",
    )
    yield page
    context.close()


# === FREE plan fixtures (for limit enforcement tests) ===

@pytest.fixture
def free_broker(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, FREE_BROKER_EMAIL, FREE_BROKER_PASSWORD,
        "FREE_BROKER_EMAIL/FREE_BROKER_PASSWORD",
    )
    yield page
    context.close()


@pytest.fixture
def free_load_owner(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, FREE_LOAD_OWNER_EMAIL, FREE_LOAD_OWNER_PASSWORD,
        "FREE_LOAD_OWNER_EMAIL/FREE_LOAD_OWNER_PASSWORD",
    )
    yield page
    context.close()


@pytest.fixture
def free_carrier(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, FREE_CARRIER_EMAIL, FREE_CARRIER_PASSWORD,
        "FREE_CARRIER_EMAIL/FREE_CARRIER_PASSWORD",
    )
    yield page
    context.close()


@pytest.fixture
def free_owner_operator(browser, browser_context_args):
    context, page = _logged_in_page(
        browser, browser_context_args, FREE_OWNER_OPERATOR_EMAIL, FREE_OWNER_OPERATOR_PASSWORD,
        "FREE_OWNER_OPERATOR_EMAIL/FREE_OWNER_OPERATOR_PASSWORD",
    )
    yield page
    context.close()


@pytest.fixture(scope="module")
def _load_owner_context(browser, browser_context_args):
    """Single load_owner session shared across a test module."""
    context, page = _logged_in_page(
        browser, browser_context_args, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD,
        "LOAD_OWNER_EMAIL/LOAD_OWNER_PASSWORD",
    )
    yield page
    context.close()


@pytest.fixture
def fresh_load_for_bid(_load_owner_context):
    """Load owner creates a fresh load, returns unique price for carrier to find it."""
    import time
    from helpers import create_load

    price = int(time.time()) % 9000 + 1000
    create_load(_load_owner_context, price)
    return price


@pytest.fixture
def landing_page(page: Page):
    """Open the landing page without logging in."""
    page.goto(_required_env("BASE_URL", BASE_URL), wait_until="domcontentloaded")
    return page
