import os
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
load_dotenv()


# Eski testlar EMAIL/PASSWORD ishlatadi — backward-compat uchun saqlanmoqda
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


def _login_as(page: Page, email: str, password: str) -> Page:
    """
    Berilgan email/password bilan login qiladi.
    Sayt login'dan keyin /loads yoki /profile/root ga tushiradi (role/account holatiga qarab).
    Tekshirish: /sign-in dan chiqib ketgan bo'lsa — login muvaffaqiyatli.
    """
    import re
    page.goto(f"{APP_URL}/sign-in?lang=en")
    page.get_by_placeholder("Email or phone number is required").fill(email)
    page.get_by_placeholder("Enter your password").fill(password)
    page.get_by_role("button", name="Sign In", exact=True).click()
    expect(page).not_to_have_url(re.compile(r".*sign-in.*"), timeout=15000)

    accept_button = page.get_by_role("button", name="Accept")
    if accept_button.is_visible():
        accept_button.click()

    return page


@pytest.fixture
def open_page(page: Page):
    """Login sahifasini ochadi, login qilmaydi"""
    page.goto(f"{APP_URL}/sign-in?lang=en")
    return page


@pytest.fixture
def logged_in(page: Page):
    """Broker bilan login qiladi (eski testlar uchun)."""
    return _login_as(page, EMAIL, PASSWORD)


@pytest.fixture
def logged_in_broker(page: Page):
    """Broker role bilan login."""
    return _login_as(page, BROKER_EMAIL, BROKER_PASSWORD)


@pytest.fixture
def logged_in_load_owner(page: Page):
    """Load owner role bilan login."""
    return _login_as(page, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD)


@pytest.fixture
def logged_in_carrier(page: Page):
    """Carrier role bilan login."""
    return _login_as(page, CARRIER_EMAIL, CARRIER_PASSWORD)


@pytest.fixture
def logged_in_owner_operator(page: Page):
    """Owner operator role bilan login."""
    return _login_as(page, OWNER_OPERATOR_EMAIL, OWNER_OPERATOR_PASSWORD)


@pytest.fixture
def landing_page(page: Page):
    """Landing sahifani login qilmasdan ochadi."""
    page.goto(BASE_URL, wait_until="domcontentloaded")
    return page
