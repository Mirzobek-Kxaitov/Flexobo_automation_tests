from playwright.sync_api import Page, expect
from conftest import BASE_URL

def test_landing_page(landing_page: Page):
    """Check if the landing page is accessible and contains the expected elements"""
    expect(landing_page).to_have_url(BASE_URL)
    expect(landing_page.get_by_text("Sign In")).to_be_visible()
    expect(landing_page.get_by_text("From?")).to_be_visible()
    expect(landing_page.get_by_text("To?")).to_be_visible()
    expect(landing_page.get_by_text("When")).to_be_visible()
    expect(landing_page.get_by_role("button", name="Search")).to_be_visible()

