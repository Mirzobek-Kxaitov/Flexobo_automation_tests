import os
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from pages.login_page import LoginPage

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


@allure.feature("Login")
@allure.story("Valid login")
def test_valid_login(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.fill_email(EMAIL).fill_password(PASSWORD).submit()
    login_page.expect_logged_in()


@allure.feature("Login")
@allure.story("Invalid credentials")
def test_invalid_login(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.fill_email("wrong@example.com").fill_password("123321").submit()
    login_page.expect_invalid_credentials()


@allure.feature("Login")
@allure.story("Empty email")
def test_empty_email(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.fill_password("123321").submit()
    expect(open_page.get_by_text("Email or phone number is required")).to_be_visible()


@allure.feature("Login")
@allure.story("Empty password")
def test_empty_password(open_page: Page):
    login_page = LoginPage(open_page)
    login_page.fill_email(EMAIL).submit()
    expect(open_page.get_by_text("Password is required")).to_be_visible()
