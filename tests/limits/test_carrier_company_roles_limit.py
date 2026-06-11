"""
Carrier — Company roles limit enforcement tests.

Scenario:
1. Carrier creates 1 company role (0 -> 1/1).
2. On the 2nd role creation attempt a 'Limit reached' modal appears.
3. Modal behaviour: 'Maybe later' closes it, 'Upgrade plan' navigates away.

Free plan: Company roles limit = 1.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from tests.helpers import create_role, read_usage_counter

load_dotenv()
APP_URL = os.getenv("APP_URL")

ROLES_LIMIT = 1


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="BUG: Company roles usage counter not incrementing after role creation")
@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: company roles limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_company_roles_limit_full_flow(logged_in_carrier: Page):
    """
    Verify that the carrier cannot create more than ROLES_LIMIT company roles
    on the free plan and that a 'Limit reached' modal is shown on the
    (ROLES_LIMIT+1)th attempt.

    Steps:
    1. Read the current roles counter from the Usage tab.
    2. Fill up to the limit by creating roles.
    3. Confirm the counter reached the limit.
    4. Attempt one more role creation and verify the modal.
    """
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Read current company roles counter from Usage tab"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        needed = max(0, ROLES_LIMIT - current)

    with allure.step(f"Fill roles up to limit (current={current}, needed={needed})"):
        for i in range(needed):
            role_num = current + i + 1
            with allure.step(f"Create role #{role_num}/{ROLES_LIMIT}"):
                create_role(page, f"Carrier Role {role_num}")

    with allure.step("Confirm roles counter reached the limit"):
        final = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        assert final >= ROLES_LIMIT, (
            f"Expected >= {ROLES_LIMIT}/{ROLES_LIMIT}, got {final}/{ROLES_LIMIT}"
        )

    with allure.step("Attempt one more role creation beyond the limit"):
        create_role(page, "Carrier Over Limit Role")

    with allure.step("Verify 'Limit reached' modal is displayed"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible()
        expect(page.get_by_text("You have reached your limit")).to_be_visible()
        expect(page.get_by_role("button", name="Upgrade plan")).to_be_visible()
        expect(page.get_by_role("button", name="Maybe later")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Carrier: company roles limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_roles_modal_maybe_later(logged_in_carrier: Page):
    """Verify that clicking 'Maybe later' closes the limit modal."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Check carrier is already at the roles limit"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        if current < ROLES_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{ROLES_LIMIT}. "
                f"Run test_carrier_company_roles_limit_full_flow first."
            )

    with allure.step("Attempt a role creation beyond the limit to trigger modal"):
        create_role(page, "Maybe Later Role")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible()

    with allure.step("Click 'Maybe later' and verify modal is dismissed"):
        page.get_by_role("button", name="Maybe later").click()
        page.wait_for_timeout(1000)
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Carrier: company roles limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_roles_modal_upgrade_plan(logged_in_carrier: Page):
    """Verify that clicking 'Upgrade plan' navigates to the pricing/upgrade page."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Check carrier is already at the roles limit"):
        current = read_usage_counter(page, "Company roles", ROLES_LIMIT)
        if current < ROLES_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{ROLES_LIMIT}. "
                f"Run test_carrier_company_roles_limit_full_flow first."
            )

    with allure.step("Attempt a role creation beyond the limit to trigger modal"):
        create_role(page, "Upgrade Plan Role")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible()

    with allure.step("Click 'Upgrade plan' and verify navigation to pricing page"):
        page.get_by_role("button", name="Upgrade plan").click()
        page.wait_for_timeout(3000)
        expect(page).to_have_url(
            re.compile(r".*(pricing|upgrade|plan).*")
        )
