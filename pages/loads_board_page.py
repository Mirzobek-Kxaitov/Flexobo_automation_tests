import re
from playwright.sync_api import Page, expect


class LoadsBoardPage:
    def __init__(self, page: Page):
        self.page = page
        self.search_from = page.get_by_test_id("loads_search_from_input")
        self.search_to = page.get_by_test_id("loads_search_to_input")
        self.search_button = page.get_by_test_id("loads_search_button")
        self.filter_button = page.get_by_test_id("loads_filter_button")
        self.filter_panel = page.get_by_test_id("loads_filter_panel")
        self.filter_apply = page.get_by_test_id("loads_filter_apply_button")
        self.filter_reset = page.get_by_test_id("loads_filter_reset_button")

    def open(self, app_url: str):
        self.page.goto(f"{app_url}/loads", wait_until="domcontentloaded")
        expect(self.search_from).to_be_visible()
        cookie = self.page.get_by_test_id("global_cookie_accept_button")
        if cookie.is_visible():
            cookie.click(force=True)
        return self

    def _dismiss_drawer(self):
        """Close any open drawer/overlay that blocks interaction."""
        drawer = self.page.locator("[data-vaul-drawer][data-state='open']")
        if drawer.is_visible():
            self.page.keyboard.press("Escape")
        return self

    def search_from_city(self, city: str):
        self.search_from.fill(city)
        suggestion = self.page.get_by_text(city, exact=False).first
        expect(suggestion).to_be_visible()
        suggestion.click(force=True)
        return self

    def click_search(self):
        self._dismiss_drawer()
        self.search_button.click()
        return self

    def open_filter_panel(self):
        self.filter_button.click()
        expect(self.filter_panel).to_be_visible()
        return self

    def expect_search_form_visible(self):
        expect(self.search_from).to_be_visible()
        expect(self.search_to).to_be_visible()
        expect(self.search_button).to_be_visible()
        expect(self.filter_button).to_be_visible()
        return self

    def expect_filter_panel_visible(self):
        expect(self.filter_panel).to_be_visible()
        expect(self.filter_apply).to_be_visible()
        expect(self.filter_reset).to_be_visible()
        return self
