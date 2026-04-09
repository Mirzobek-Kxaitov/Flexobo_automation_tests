from playwright.sync_api import Page
from pages.landing_page import LandingPage


def test_landing_page(landing_page: Page):
    LandingPage(landing_page).expect_page_loaded().expect_all_elements_visible()
