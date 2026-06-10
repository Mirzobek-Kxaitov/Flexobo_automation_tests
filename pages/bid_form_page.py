from playwright.sync_api import Page, expect


class BidFormPage:
    def __init__(self, page: Page):
        self.page = page
        self.container = page.get_by_test_id("bid_form_container")
        self.note_input = page.get_by_test_id("bid_form_note_input")
        self.date_button = page.get_by_test_id("bid_form_date_button")
        self.submit_button = page.get_by_test_id("bid_form_submit_button")
        self.cancel_button = page.get_by_test_id("bid_form_cancel_button")
        self.open_button = page.get_by_test_id("bid_place_open_button")

    def open_form(self):
        expect(self.open_button).to_be_visible(timeout=10000)
        self.open_button.click()
        expect(self.container).to_be_visible(timeout=10000)
        return self

    def fill_note(self, text: str):
        self.note_input.fill(text)
        return self

    def submit(self):
        self.submit_button.click()
        return self

    def cancel(self):
        self.cancel_button.click()
        expect(self.note_input).not_to_be_visible(timeout=5000)
        return self

    def expect_form_visible(self):
        expect(self.container).to_be_visible()
        expect(self.note_input).to_be_visible()
        expect(self.date_button).to_be_visible()
        expect(self.submit_button).to_be_visible()
        return self

    def expect_form_hidden(self):
        expect(self.container).not_to_be_visible(timeout=5000)
        return self
