import os
import re
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL")

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        #locators
        self.sign_in_link = page.get_by_text("Sign In")
        self.email_input = page.get_by_placeholder("Email or phone number is required")
        self.password_input = page.get_by_placeholder("Enter your password")
        self.sign_in_button = page.get_by_role("button", name="Sign In", exact=True)
        self.error_message = page.get_by_text("Invalid phone number or email")

    def open(self):
        self.page.goto(BASE_URL, wait_until="domcontentloaded")
        return self
    
    def click_sign_in(self):
        self.sign_in_link.click()
        return self
    
    def fill_email(self, email):
        self.email_input.fill(email)
        return self
    
    def fill_password(self, password):
        self.password_input.fill(password)
        return self
    
    def submit(self):
        self.sign_in_button.click()
        return self
    
    def login(self, email, password):
        self.open()
        self.click_sign_in()
        self.fill_email(email)
        self.fill_password(password)
        self.submit()
        return self
    
    def expect_logged_in(self):
        expect(self.page).not_to_have_url(re.compile(r".*sign-in.*"), timeout=15000)
        return self
    
    def expect_invalid_credentials(self):
        expect(self.error_message).to_be_visible()
        return self
    