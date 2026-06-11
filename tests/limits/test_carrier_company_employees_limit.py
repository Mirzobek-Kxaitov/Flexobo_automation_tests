"""
Carrier — Company employees limit enforcement tests.

Scenario:
1. Carrier invites 2 employees (0 -> 2/2).
2. On the 3rd invitation attempt a 'Limit reached' modal appears.
3. Modal behaviour: 'Maybe later' closes it, 'Upgrade plan' navigates away.

Free plan: Company employees limit = 2.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from tests.helpers import invite_employee, read_usage_counter

load_dotenv()
APP_URL = os.getenv("APP_URL")

EMPLOYEES_LIMIT = 2


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="BUG: Company employees usage counter not incrementing after invitation")
@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: company employees limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_company_employees_limit_full_flow(logged_in_carrier: Page):
    """
    Verify that the carrier cannot invite more than EMPLOYEES_LIMIT employees
    on the free plan and that a 'Limit reached' modal is shown on the
    (EMPLOYEES_LIMIT+1)th attempt.

    Steps:
    1. Read the current employees counter from the Usage tab.
    2. Fill up to the limit by inviting employees.
    3. Confirm the counter reached the limit.
    4. Attempt one more invitation and verify the modal.
    """
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Read current company employees counter from Usage tab"):
        current = read_usage_counter(page, "Company employees", EMPLOYEES_LIMIT)
        needed = max(0, EMPLOYEES_LIMIT - current)

    with allure.step(f"Fill employees up to limit (current={current}, needed={needed})"):
        for i in range(needed):
            num = current + i + 1
            with allure.step(f"Invite employee #{num}/{EMPLOYEES_LIMIT}"):
                invite_employee(page, num, prefix="carrier_emp")

    with allure.step("Confirm employees counter reached the limit"):
        final = read_usage_counter(page, "Company employees", EMPLOYEES_LIMIT)
        assert final >= EMPLOYEES_LIMIT, (
            f"Expected >= {EMPLOYEES_LIMIT}/{EMPLOYEES_LIMIT}, got {final}/{EMPLOYEES_LIMIT}"
        )

    with allure.step("Attempt one more invitation beyond the limit"):
        invite_employee(page, EMPLOYEES_LIMIT + 1, prefix="carrier_emp")

    with allure.step("Verify 'Limit reached' modal is displayed"):
        expect(
            page.get_by_role("heading", name="Limit reached")
        ).to_be_visible()
        expect(page.get_by_text("You have reached your limit")).to_be_visible()
        expect(page.get_by_role("button", name="Upgrade plan")).to_be_visible()
        expect(page.get_by_role("button", name="Maybe later")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Carrier: company employees limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_employees_modal_maybe_later(logged_in_carrier: Page):
    """Verify that clicking 'Maybe later' closes the limit modal."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Check carrier is already at the employees limit"):
        current = read_usage_counter(page, "Company employees", EMPLOYEES_LIMIT)
        if current < EMPLOYEES_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{EMPLOYEES_LIMIT}. "
                f"Run test_carrier_company_employees_limit_full_flow first."
            )

    with allure.step("Attempt an invitation beyond the limit to trigger modal"):
        invite_employee(page, 9001, prefix="carrier_emp")

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
@allure.story("Carrier: company employees limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_employees_modal_upgrade_plan(logged_in_carrier: Page):
    """Verify that clicking 'Upgrade plan' navigates to the pricing/upgrade page."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Check carrier is already at the employees limit"):
        current = read_usage_counter(page, "Company employees", EMPLOYEES_LIMIT)
        if current < EMPLOYEES_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{EMPLOYEES_LIMIT}. "
                f"Run test_carrier_company_employees_limit_full_flow first."
            )

    with allure.step("Attempt an invitation beyond the limit to trigger modal"):
        invite_employee(page, 9002, prefix="carrier_emp")

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
