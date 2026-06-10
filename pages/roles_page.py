import os
import re
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")


class RolesPage:

    PROFILE_URL = f"{APP_URL}/profile/root"

    def __init__(self, page: Page):
        self.page = page

        self.roles_tab = page.get_by_test_id("profile_roles_tab")
        self.users_tab = page.get_by_test_id("profile_users_tab")

        self.create_role_button = page.get_by_test_id("roles_create_button")
        self.role_name_input = page.get_by_test_id("roles_name_input").or_(
            page.get_by_role("textbox", name="Role name")
        ).first
        self.update_role_button = page.get_by_test_id("roles_submit_button").or_(
            page.get_by_role("button", name="Update Role")
        ).first

        self.confirm_delete_button = page.get_by_test_id("roles_delete_confirm_button").or_(
            page.get_by_role("button", name="Delete")
        ).first

    def go_to_roles(self) -> "RolesPage":
        self.page.goto(self.PROFILE_URL, wait_until="domcontentloaded")
        expect(self.roles_tab).to_be_visible(timeout=10000)
        self.roles_tab.click()
        expect(self.create_role_button).to_be_visible(timeout=10000)
        return self

    def _dismiss_cookie_banner(self) -> "RolesPage":
        btn = self.page.get_by_test_id("global_cookie_accept_button")
        if btn.is_visible(timeout=1000):
            btn.click(force=True)
        return self

    def create_role(self, name: str) -> "RolesPage":
        self.go_to_roles()
        self._dismiss_cookie_banner()
        self.create_role_button.click()
        expect(self.role_name_input).to_be_visible(timeout=10000)
        self.role_name_input.fill(name)
        self.update_role_button.click(force=True)
        expect(self.page.get_by_text(name).first).to_be_visible(timeout=10000)
        return self

    def _get_role_card(self, name: str):
        return self.page.locator("div").filter(has_text=re.compile(rf"^{re.escape(name)}")).first

    def _open_role_delete(self, name: str) -> "RolesPage":
        card = self._get_role_card(name)
        delete_button = card.locator("[data-testid^='roles_delete_button_']")
        if delete_button.count() > 0:
            delete_button.first.click()
        else:
            card.locator("button[data-slot='alert-dialog-trigger']").click()
        return self

    def delete_role(self, name: str) -> "RolesPage":
        self.go_to_roles()
        self._open_role_delete(name)
        self.confirm_delete_button.click()
        return self

    def expect_role_visible(self, name: str) -> "RolesPage":
        expect(self.page.get_by_text(name).first).to_be_visible(timeout=10000)
        return self

    def expect_role_not_visible(self, name: str) -> "RolesPage":
        expect(self.page.get_by_text(name)).not_to_be_visible(timeout=10000)
        return self

    def expect_on_roles_tab(self) -> "RolesPage":
        expect(self.roles_tab).to_be_visible()
        return self
