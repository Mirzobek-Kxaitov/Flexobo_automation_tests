import os
from playwright.sync_api import Page
from dotenv import load_dotenv
from playwright.sync_api import expect
from pages.login_page import LoginPage
load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def test_valid_login(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.login(EMAIL, PASSWORD).submit()
    login_page.expect_logged_in()

def test_invalid_login(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.login("wrong@example.com", "123321").submit()
    login_page.expect_invalid_credentials()


def test_empty_email(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.fill_password("123321").submit()
    expect(open_page.get_by_text("Email or phone number is required")).to_be_visible()

def test_empty_password(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.fill_email(EMAIL).submit()
    expect(open_page.get_by_text("Password is required")).to_be_visible()  
    