import os
import re
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")


class UsersPage:

    USERS_URL = f"{APP_URL}/company-users"
    PROFILE_URL = f"{APP_URL}/profile/root"

    def __init__(self, page: Page):
        self.page = page

        # Tabs
        self.users_tab = page.get_by_role("tab", name="Users")
        self.pending_tab = page.get_by_role("tab", name="Pending Invitations")

        # Invite form
        self.invite_button = page.get_by_role("button", name="Invite User")
        self.email_input = page.get_by_role("textbox", name="Phone or Email")
        self.role_combobox = page.get_by_role("combobox", name="Role")
        self.send_button = page.get_by_role("button", name="Send Invitation")

        # Pending actions
        self.cancel_invitation_button = page.get_by_role("button", name="Cancel Invitation")

        # Messages
        self.resent_message = page.get_by_text("Invitation resent successfully")
        self.no_pending_message = page.get_by_text("No pending invitations")

    # ── Navigation ──────────────────────────────────────────────

    def go_to_users(self):
        self.page.goto(self.PROFILE_URL)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.users_tab.click()
        self.page.wait_for_timeout(2000)
        return self

    def go_to_pending(self):
        self.page.goto(self.USERS_URL)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)
        self.page.get_by_role("tab", name="Pending Invitations").click()
        self.page.wait_for_timeout(2000)
        return self

    def _dismiss_cookie_banner(self):
        btn = self.page.get_by_role("button", name="Accept")
        if btn.is_visible(timeout=1000):
            btn.click(force=True)
            self.page.wait_for_timeout(500)
        return self

    # ── Invite ──────────────────────────────────────────────────

    def invite_user(self, email, role_name=None):
        self.go_to_users()
        self._dismiss_cookie_banner()
        self.invite_button.click()
        self.page.wait_for_timeout(1000)
        self.email_input.fill(email)
        self.role_combobox.click()
        if role_name:
            self.page.get_by_role("option", name=role_name).click()
        else:
            self.page.get_by_role("option").first.click()
        self.page.wait_for_timeout(500)
        self.send_button.click()
        self.page.wait_for_timeout(3000)
        # Dismiss any overlay (success toast, limit modal, etc.)
        self.page.locator(".fixed").first.click(force=True, timeout=2000)
        self.page.wait_for_timeout(1000)
        return self

    # ── Pending Invitations ─────────────────────────────────────

    def resend_invitation(self, email):
        self.go_to_pending()
        self.page.get_by_text(email).first.click()
        self.page.wait_for_timeout(1000)
        self.page.get_by_role("button", name="Resend").first.click()
        self.page.wait_for_timeout(2000)
        return self

    def cancel_invitation(self, email):
        self.go_to_pending()
        self.page.locator("button[data-slot='alert-dialog-trigger']").first.click()
        self.page.wait_for_timeout(500)
        self.cancel_invitation_button.click()
        self.page.wait_for_timeout(2000)
        return self

    # ── Assertions ──────────────────────────────────────────────

    def expect_invitation_visible(self, email):
        self.go_to_pending()
        expect(self.page.get_by_text(email).first).to_be_visible(timeout=10000)
        return self

    def expect_resent_success(self):
        expect(self.resent_message).to_be_visible(timeout=10000)
        return self

    def expect_no_pending(self):
        expect(self.no_pending_message).to_be_visible(timeout=10000)
        return self

    def expect_on_users_tab(self):
        expect(self.users_tab).to_be_visible()
        return self
