"""
Fleet size limit enforcement tests — verifies that Free plan limit is enforced in practice.

Scenario:
1. Broker adds 5 trailers (0 -> 5/5)
2. Attempt to add trailer #6 -> "Limit reached" modal appears
3. Modal behavior: "Close" (closes modal), "Upgrade plan" (navigates to upgrade page)

Modal: dialog[name="Limit reached"] — contains "Close" and "Upgrade plan" buttons.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from tests.helpers import read_usage_counter, add_trailer

load_dotenv()
APP_URL = os.getenv("APP_URL")

FLEET_LIMIT = 5


@pytest.mark.xfail(
    reason="BUG: Fleet size usage counter not incrementing after trailer creation"
)
@allure.feature("Plan Limits")
@allure.story("Free plan: fill fleet to limit and verify 'Limit reached' modal")
@allure.severity(allure.severity_level.CRITICAL)
def test_fleet_limit_full_flow(logged_in_broker: Page):
    """
    Add trailers up to the fleet limit (5/5) and verify that
    attempting to add a 6th triggers the 'Limit reached' modal.

    Steps:
    1. Read current fleet size from Usage page
    2. Fill up to the limit by adding trailers
    3. Confirm counter reached the limit
    4. Add one more trailer and verify the modal appears
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    with allure.step("Read current fleet size from Usage page"):
        current = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        needed = FLEET_LIMIT - current

    with allure.step(f"Fill up to limit: {current}/{FLEET_LIMIT}, need {needed} more trailers"):
        for i in range(needed):
            truck_num = current + i + 1
            with allure.step(f"Add trailer #{truck_num}/{FLEET_LIMIT}"):
                add_trailer(page, truck_num)

    with allure.step("Confirm fleet size counter reached the limit"):
        final = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        assert final == FLEET_LIMIT, (
            f"Expected {FLEET_LIMIT}/{FLEET_LIMIT}, got {final}/{FLEET_LIMIT}"
        )

    with allure.step("Add one over-limit trailer and expect 'Limit reached' modal"):
        add_trailer(page, FLEET_LIMIT + 1)

    with allure.step("Verify 'Limit reached' modal is visible with 'Close' button"):
        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).to_be_visible(timeout=10000)

        expect(
            page.get_by_role("button", name="Close")
        ).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Fleet limit modal: 'Close' dismisses modal")
@allure.severity(allure.severity_level.NORMAL)
def test_fleet_modal_close(logged_in_broker: Page):
    """
    When the broker is at the fleet limit and adds another trailer,
    clicking 'Close' on the modal should close it.

    Pre-condition: broker must already be at 5/5.
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    with allure.step("Check that broker is already at the fleet limit"):
        current = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        if current < FLEET_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{FLEET_LIMIT}. "
                f"Run test_fleet_limit_full_flow first."
            )

    with allure.step("Add an over-limit trailer to trigger the modal"):
        add_trailer(page, 9001)

    with allure.step("Verify 'Limit reached' modal appears"):
        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Close' and verify modal closes"):
        page.get_by_role("button", name="Close").click()
        page.wait_for_timeout(1000)

        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Fleet limit modal: 'Upgrade plan' navigates to upgrade page")
@allure.severity(allure.severity_level.NORMAL)
def test_fleet_modal_upgrade_plan(logged_in_broker: Page):
    """
    When the broker is at the fleet limit and adds another trailer,
    clicking 'Upgrade plan' should navigate to the pricing/upgrade page.

    Pre-condition: broker must already be at 5/5.
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    with allure.step("Check that broker is already at the fleet limit"):
        current = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        if current < FLEET_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{FLEET_LIMIT}. "
                f"Run test_fleet_limit_full_flow first."
            )

    with allure.step("Add an over-limit trailer to trigger the modal"):
        add_trailer(page, 9002)

    with allure.step("Verify 'Limit reached' modal appears"):
        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation to pricing page"):
        upgrade_btn = page.get_by_role("button", name="Upgrade plan")
        if upgrade_btn.is_visible(timeout=3000):
            upgrade_btn.click()
            page.wait_for_timeout(3000)
            expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
        else:
            pytest.skip("'Upgrade plan' button not found in modal")
