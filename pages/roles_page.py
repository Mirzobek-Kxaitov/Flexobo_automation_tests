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

        # Tabs
        self.roles_tab = page.get_by_role("tab", name="Roles")
        self.users_tab = page.get_by_role("tab", name="Users")

        # Role form
        self.create_role_button = page.get_by_role("button", name="Create role")
        self.role_name_input = page.get_by_role("textbox", name="Role name")
        self.update_role_button = page.get_by_role("button", name="Update Role")

        # Confirm dialogs
        self.confirm_delete_button = page.get_by_role("button", name="Delete")

    # ── Navigation ──────────────────────────────────────────────

    def go_to_roles(self):
        self.page.goto(self.PROFILE_URL)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.roles_tab.click()
        self.page.wait_for_timeout(1500)
        return self

    # ── CRUD ────────────────────────────────────────────────────

    def _dismiss_cookie_banner(self):
        btn = self.page.get_by_role("button", name="Accept")
        if btn.is_visible(timeout=1000):
            btn.click(force=True)
            self.page.wait_for_timeout(500)
        return self

    def create_role(self, name):
        self.go_to_roles()
        self._dismiss_cookie_banner()
        self.create_role_button.click()
        self.page.wait_for_timeout(1000)
        self.role_name_input.fill(name)
        self.create_role_button.click(force=True)
        self.page.wait_for_timeout(3000)
        return self

    def _get_role_card(self, name):
        return self.page.locator("div").filter(has_text=re.compile(rf"^{re.escape(name)}")).first

    def _open_role_delete(self, name):
        """Click the delete (trash) button on a role card."""
        card = self._get_role_card(name)
        card.locator("button[data-slot='alert-dialog-trigger']").click()
        self.page.wait_for_timeout(500)
        return self

    def delete_role(self, name):
        self.go_to_roles()
        self._open_role_delete(name)
        self.confirm_delete_button.click()
        self.page.wait_for_timeout(2000)
        return self

    # ── Assertions ──────────────────────────────────────────────

    def expect_role_visible(self, name):
        expect(self.page.get_by_text(name).first).to_be_visible(timeout=10000)
        return self

    def expect_role_not_visible(self, name):
        expect(self.page.get_by_text(name)).not_to_be_visible(timeout=10000)
        return self

    def expect_on_roles_tab(self):
        expect(self.roles_tab).to_be_visible()
        return self
