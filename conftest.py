import os
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
load_dotenv()


EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = os.getenv("BASE_URL")

@pytest.fixture
def open_page(page: Page):
    """Faqat landing sahifasini ochadi, login qilmaydi"""
    page.goto(BASE_URL,wait_until="domcontentloaded")
    page.get_by_text("Sign In").click()
    return page

@pytest.fixture
def logged_in(page: Page):
    """Login qilib, tayyor page qaytaradi"""
    page.goto(BASE_URL)
    page.get_by_text("Sign In").click()
    page.get_by_placeholder("Email or phone number is required").fill(EMAIL)
    page.get_by_placeholder("Enter your password").fill(PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    expect(page).to_have_url(BASE_URL)

    #coockie
    accept_button = page.get_by_role("button", name="Accept")
    if accept_button.is_visible():
        accept_button.click()
    
    return page

@pytest.fixture
def landing_page(page: Page):
    """will open the landing page without logging in"""
    page.goto(BASE_URL)
    return page