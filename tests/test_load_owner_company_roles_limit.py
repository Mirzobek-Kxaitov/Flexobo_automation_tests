"""Load Owner — Company roles limit enforcement tests.

Scenario:
1. Load owner creates 1 company role (0 -> 1/1).
2. Attempt to create a 2nd role -> "Limit reached" modal appears.
3. Modal behavior: "Maybe later" (dismisses), "Upgrade plan" (navigates).

Free plan: Company roles limit = 1.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from helpers import create_role, read_usage_counter

load_dotenv()
APP_URL = os.getenv("APP_URL")

ROLES_LIMIT = 1


@pytest.mark.xfail(reason="BUG: Company roles usage counter not incrementing after role creation")
@allure.feature("Plan Limits")
@allure.story("Load Owner Free plan: company roles limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_company_roles_limit_full_flow(logged_in_load_owner: Page):
    """Verify that creating a 2nd role triggers the 'Limit reached' modal."""
    page = logged_in_load_owner
    page.set_default_timeout(60000)

    with allure.step("Read current company roles counter from Usage tab"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        needed = ROLES_LIMIT - current

    with allure.step(f"Create {needed} role(s) to reach the limit"):
        for i in range(needed):
            role_num = current + i + 1
            create_role(page, f"LO Test Role {role_num}")

    with allure.step("Verify counter has reached the limit"):
        final = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        assert final >= ROLES_LIMIT, (
            f"Expected >= {ROLES_LIMIT}/{ROLES_LIMIT}, got {final}/{ROLES_LIMIT}"
        )

    with allure.step("Attempt to create one more role (over-limit)"):
        create_role(page, "LO Over Limit Role")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)
        expect(page.get_by_text("You have reached your limit")).to_be_visible()
        expect(page.get_by_role("button", name="Upgrade plan")).to_be_visible()
        expect(page.get_by_role("button", name="Maybe later")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Load Owner: company roles limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_load_owner_company_roles_modal_maybe_later(logged_in_load_owner: Page):
    """Verify that clicking 'Maybe later' closes the limit modal."""
    page = logged_in_load_owner
    page.set_default_timeout(60000)

    with allure.step("Check current roles counter"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        if current < ROLES_LIMIT:
            pytest.skip(
                f"Load owner is at {current}/{ROLES_LIMIT}. "
                f"Run test_load_owner_company_roles_limit_full_flow first."
            )

    with allure.step("Trigger 'Limit reached' modal"):
        create_role(page, "LO Maybe Later Role")
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Maybe later' and verify modal is dismissed"):
        page.get_by_role("button", name="Maybe later").click()
        page.wait_for_timeout(1000)
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Load Owner: company roles limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_load_owner_company_roles_modal_upgrade_plan(logged_in_load_owner: Page):
    """Verify that clicking 'Upgrade plan' navigates to the upgrade page."""
    page = logged_in_load_owner
    page.set_default_timeout(60000)

    with allure.step("Check current roles counter"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        if current < ROLES_LIMIT:
            pytest.skip(
                f"Load owner is at {current}/{ROLES_LIMIT}. "
                f"Run test_load_owner_company_roles_limit_full_flow first."
            )

    with allure.step("Trigger 'Limit reached' modal"):
        create_role(page, "LO Upgrade Plan Role")
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation to upgrade page"):
        page.get_by_role("button", name="Upgrade plan").click()
        page.wait_for_timeout(3000)
        expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
