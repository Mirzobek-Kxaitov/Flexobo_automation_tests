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

        self.users_tab = page.get_by_test_id("profile_users_tab")
        self.pending_tab = page.get_by_test_id("users_pending_invitations_tab")

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

        self.cancel_invitation_button = page.get_by_role("alertdialog").get_by_role(
            "button", name="Cancel Invitation"
        )

        self.resent_message = page.get_by_text("Invitation resent successfully")
        self.no_pending_message = page.get_by_text("No pending invitations")

    def go_to_users(self) -> "UsersPage":
        self.page.goto(self.PROFILE_URL, wait_until="domcontentloaded")
        expect(self.users_tab).to_be_visible()
        self.users_tab.click()
        expect(self.invite_button).to_be_visible()
        return self

    def go_to_pending(self) -> "UsersPage":
        self.page.goto(self.USERS_URL, wait_until="domcontentloaded")
        expect(self.pending_tab).to_be_visible()
        self.pending_tab.click()
        return self

    def _dismiss_cookie_banner(self) -> "UsersPage":
        btn = self.page.get_by_test_id("global_cookie_accept_button")
        if btn.is_visible():
            btn.click(force=True)
        return self

    def invite_user(self, email: str, role_name: str = None) -> "UsersPage":
        self.go_to_users()
        self._dismiss_cookie_banner()
        self.invite_button.click()
        expect(self.email_input).to_be_visible()
        self.email_input.fill(email)
        self.role_combobox.click()
        if role_name:
            self.page.get_by_role("option", name=role_name).click()
        else:
            self.page.get_by_role("option").first.click()
        self.send_button.click()
        self.page.wait_for_timeout(2000)
        return self

    def resend_invitation(self, email: str) -> "UsersPage":
        self.go_to_pending()
        self.page.get_by_text(email).first.click()
        resend_btn = self.page.get_by_role("button", name="Resend").first
        expect(resend_btn).to_be_visible()
        resend_btn.click()
        return self

    def cancel_invitation(self, email: str) -> "UsersPage":
        self.last_cancelled_email = email
        self.go_to_pending()
        cancel_button = self.page.locator("[data-testid^='users_cancel_button_']")
        if cancel_button.count() > 0:
            cancel_button.first.click()
        else:
            self.page.locator("button[data-slot='alert-dialog-trigger']").first.click()
        expect(self.cancel_invitation_button).to_be_visible()
        self.cancel_invitation_button.click()
        return self

    def expect_invitation_visible(self, email: str) -> "UsersPage":
        self.go_to_pending()
        expect(self.page.get_by_text(email).first).to_be_visible()
        return self

    def expect_resent_success(self) -> "UsersPage":
        expect(self.resent_message).to_be_visible()
        return self

    def expect_no_pending(self) -> "UsersPage":
        if self.no_pending_message.is_visible():
            return self
        email = getattr(self, "last_cancelled_email", None)
        assert email, "No cancelled email recorded for pending invitation check"
        expect(self.page.get_by_text(email).first).not_to_be_visible()
        return self

    def expect_on_users_tab(self) -> "UsersPage":
        expect(self.users_tab).to_be_visible()
        return self
