import os
import re
import sys
import pytest
from playwright.sync_api import Page, expect
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

DEFAULT_TIMEOUT_MS = 30_000


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


def _logged_in_page(browser, browser_context_args, email, password, label):
    """Create a separate browser context and log in."""
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    login_as(page, email, password, label)
    return context, page


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
    from tests.helpers import create_load

    price = int(time.time()) % 9000 + 1000
    create_load(_load_owner_context, price)
    return price


@pytest.fixture
def landing_page(page: Page):
    """Open the landing page without logging in."""
    page.goto(_required_env("BASE_URL", BASE_URL), wait_until="domcontentloaded")
    return page
