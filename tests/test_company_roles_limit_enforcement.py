"""
Company roles limit enforcement tests — verifies that Free plan limit is enforced in practice.

Scenario:
1. Broker creates 1 company role (0 -> 1/1)
2. Attempt to create role #2 -> "Limit reached" modal appears
3. Modal behavior: "Maybe later" (closes modal), "Upgrade plan" (navigates to upgrade page)

Free plan: Company roles limit = 1.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import read_usage_counter, create_role

load_dotenv()
APP_URL = os.getenv("APP_URL")

ROLES_LIMIT = 1


@pytest.mark.xfail(
    reason="BUG: Company roles usage counter not incrementing after role creation"
)
@allure.feature("Plan Limits")
@allure.story("Free plan: fill company roles to limit and verify 'Limit reached' modal")
@allure.severity(allure.severity_level.CRITICAL)
def test_company_roles_limit_full_flow(logged_in_broker: Page):
    """
    Create roles up to the company roles limit (1/1) and verify that
    attempting to create a 2nd role triggers the 'Limit reached' modal.

    Steps:
    1. Read current role count from Usage page
    2. Fill up to the limit by creating roles
    3. Confirm counter reached the limit
    4. Create one more role and verify the modal appears
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    with allure.step("Read current company roles count from Usage page"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        needed = ROLES_LIMIT - current

    with allure.step(f"Fill up to limit: {current}/{ROLES_LIMIT}, need {needed} more roles"):
        for i in range(needed):
            role_num = current + i + 1
            with allure.step(f"Create role #{role_num}/{ROLES_LIMIT}"):
                create_role(page, f"Test Role {role_num}")

    with allure.step("Confirm company roles counter reached the limit"):
        final = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        assert final == ROLES_LIMIT, (
            f"Expected {ROLES_LIMIT}/{ROLES_LIMIT}, got {final}/{ROLES_LIMIT}"
        )

    with allure.step("Create one over-limit role and expect 'Limit reached' modal"):
        create_role(page, "Over Limit Role")

    with allure.step("Verify 'Limit reached' modal is visible with expected buttons"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

        expect(
            page.get_by_text("You have reached your limit")
        ).to_be_visible()

        expect(
            page.get_by_role("button", name="Upgrade plan")
        ).to_be_visible()

        expect(
            page.get_by_role("button", name="Maybe later")
        ).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Company roles limit modal: 'Maybe later' dismisses modal")
@allure.severity(allure.severity_level.NORMAL)
def test_company_roles_modal_maybe_later(logged_in_broker: Page):
    """
    When the broker is at the roles limit and creates another role,
    clicking 'Maybe later' on the modal should close it.

    Pre-condition: broker must already be at 1/1.
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    with allure.step("Check that broker is already at the company roles limit"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        if current < ROLES_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{ROLES_LIMIT}. "
                f"Run test_company_roles_limit_full_flow first."
            )

    with allure.step("Create an over-limit role to trigger the modal"):
        create_role(page, "Maybe Later Test Role")

    with allure.step("Verify 'Limit reached' modal appears"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Maybe later' and verify modal closes"):
        page.get_by_role("button", name="Maybe later").click()
        page.wait_for_timeout(1000)

        expect(
            page.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Company roles limit modal: 'Upgrade plan' navigates to upgrade page")
@allure.severity(allure.severity_level.NORMAL)
def test_company_roles_modal_upgrade_plan(logged_in_broker: Page):
    """
    When the broker is at the roles limit and creates another role,
    clicking 'Upgrade plan' should navigate to the pricing/upgrade page.

    Pre-condition: broker must already be at 1/1.
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    with allure.step("Check that broker is already at the company roles limit"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        if current < ROLES_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{ROLES_LIMIT}. "
                f"Run test_company_roles_limit_full_flow first."
            )

    with allure.step("Create an over-limit role to trigger the modal"):
        create_role(page, "Upgrade Plan Test Role")

    with allure.step("Verify 'Limit reached' modal appears"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation to pricing page"):
        page.get_by_role("button", name="Upgrade plan").click()
        page.wait_for_timeout(3000)

        expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
