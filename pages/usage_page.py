import re
from playwright.sync_api import Page, expect


class UsagePage:
    def __init__(self, page: Page):
        self.page = page
        self.usage_page = page.get_by_test_id("usage_page")
        self.current_plan_label = page.get_by_test_id("usage_current_plan_label")
        self.upgrade_plan_button = page.get_by_test_id("usage_upgrade_plan_button")

    def open(self, app_url: str):
        self.page.goto(f"{app_url}/profile/root", wait_until="domcontentloaded")
        usage_link = self.page.get_by_test_id("sidebar_usage_link").or_(
            self.page.get_by_text("Usage", exact=True)
        ).first
        expect(usage_link).to_be_visible(timeout=10000)
        usage_link.click()
        expect(self.usage_page).to_be_visible(timeout=15000)
        return self

    def get_card(self, test_id: str):
        return self.page.get_by_test_id(test_id)

    def read_counter(self, test_id: str, limit: int) -> int:
        card = self.get_card(test_id)
        text = card.inner_text(timeout=10000)
        match = re.search(rf"(\d+)\s*/\s*{limit}", text)
        assert match, f"Counter not found in card text:\n{text}"
        return int(match.group(1))

    def expect_visible(self):
        expect(self.usage_page).to_be_visible(timeout=10000)
        return self

    def expect_plan(self, plan_name: str):
        expect(self.current_plan_label).to_contain_text(plan_name, timeout=10000)
        return self

    def expect_upgrade_button_visible(self):
        expect(self.upgrade_plan_button).to_be_visible(timeout=10000)
        return self

    def expect_card_has_limit(self, test_id: str, limit_text: str):
        card = self.get_card(test_id)
        expect(card).to_be_visible(timeout=10000)
        expect(card).to_contain_text(limit_text)
        return self
