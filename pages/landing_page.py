import os
from playwright.sync_api import Page,expect
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL")

class LandingPage:
    def __init__(self, page: Page):
        self.page = page
        #locators
        self.sign_in_text = page.get_by_text("Sign In")
        self.from_text = page.get_by_text("From?")
        self.to_text = page.get_by_text("To?")
        self.when_text = page.get_by_text("When")
        self.search_button = page.get_by_role("button", name="Search")

    def open(self):
        self.page.goto(BASE_URL)
        return self
    
    def expect_page_loaded(self):
        expect(self.page).to_have_url(BASE_URL)
        return self

    def expect_all_elements_visible(self):
        expect(self.sign_in_text).to_be_visible()
        expect(self.from_text).to_be_visible()
        expect(self.to_text).to_be_visible()
        expect(self.when_text).to_be_visible()
        expect(self.search_button).to_be_visible()
        return self
    
