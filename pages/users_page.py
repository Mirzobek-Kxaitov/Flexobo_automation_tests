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
        self.users_tab = page.get_by_test_id("profile_users_tab")
        self.pending_tab = page.get_by_test_id("users_pending_invitations_tab")

        # Invite form
        self.invite_button = page.get_by_test_id("users_invite_button")
        self.email_input = page.get_by_test_id("users_invite_email_input").or_(
            page.get_by_role("textbox", name="Phone or Email")
        ).first
        self.role_combobox = page.get_by_test_id("users_invite_role_select").or_(
            page.get_by_role("combobox", name="Role")
        ).first
        self.send_button = page.get_by_test_id("users_send_invitation_button").or_(
            page.get_by_role("button", name="Send Invitation")
        ).first

        # Pending actions
        self.cancel_invitation_button = page.get_by_role("alertdialog").get_by_role(
            "button", name="Cancel Invitation"
        )

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
        self.pending_tab.click()
        self.page.wait_for_timeout(2000)
        return self

    def _dismiss_cookie_banner(self):
        btn = self.page.get_by_test_id("global_cookie_accept_button")
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
        overlay = self.page.locator(".fixed").first
        if overlay.is_visible(timeout=2000):
            overlay.click(force=True)
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
        self.last_cancelled_email = email
        self.go_to_pending()
        cancel_button = self.page.locator("[data-testid^='users_cancel_button_']")
        if cancel_button.count() > 0:
            cancel_button.first.click()
        else:
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
        if self.no_pending_message.is_visible(timeout=3000):
            return self
        email = getattr(self, "last_cancelled_email", None)
        assert email, "No cancelled email recorded for pending invitation check"
        expect(self.page.get_by_text(email).first).not_to_be_visible(timeout=10000)
        return self

    def expect_on_users_tab(self):
        expect(self.users_tab).to_be_visible()
        return self
