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
        expect(self.search_from).to_be_visible(timeout=15000)
        return self

    def search_from_city(self, city: str):
        self.search_from.fill(city)
        self.page.get_by_text(city, exact=False).first.click()
        return self

    def click_search(self):
        self.search_button.click()
        return self

    def open_filter_panel(self):
        self.filter_button.click()
        expect(self.filter_panel).to_be_visible(timeout=10000)
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
