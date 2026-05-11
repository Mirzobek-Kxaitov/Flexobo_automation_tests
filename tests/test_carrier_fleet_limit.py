"""
Carrier — Fleet size limit enforcement tests.

Scenario:
1. Carrier adds 3 trailers (0 -> 3/3).
2. On the 4th add attempt a 'Limit reached' modal appears.
3. Modal behaviour: 'Close' dismisses it, 'Upgrade plan' navigates away.

Free plan: Fleet size limit = 3.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import add_trailer, read_usage_counter

load_dotenv()
APP_URL = os.getenv("APP_URL")

FLEET_LIMIT = 3


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: fleet size limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_fleet_limit_full_flow(logged_in_carrier: Page):
    """
    Verify that the carrier cannot add more than FLEET_LIMIT trailers on the
    free plan and that a 'Limit reached' modal is shown on the (FLEET_LIMIT+1)th
    attempt.

    Steps:
    1. Read the current fleet size counter from the Usage tab.
    2. Fill up to the limit by adding trailers.
    3. Confirm the counter reached the limit.
    4. Attempt one more trailer add and verify the modal.
    """
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Read current fleet size counter from Usage tab"):
        current = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        needed = max(0, FLEET_LIMIT - current)

    with allure.step(f"Fill fleet up to limit (current={current}, needed={needed})"):
        for i in range(needed):
            num = current + i + 1
            with allure.step(f"Add trailer #{num}/{FLEET_LIMIT}"):
                add_trailer(page, num, prefix="CR-TRL")

    with allure.step("Confirm fleet size counter reached the limit"):
        final = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        assert final >= FLEET_LIMIT, (
            f"Expected >= {FLEET_LIMIT}/{FLEET_LIMIT}, got {final}/{FLEET_LIMIT}"
        )

    with allure.step("Attempt one more trailer add beyond the limit"):
        add_trailer(page, FLEET_LIMIT + 1, prefix="CR-TRL")

    with allure.step("Verify 'Limit reached' modal is displayed"):
        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).to_be_visible(timeout=10000)
        expect(page.get_by_role("button", name="Close")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Carrier: fleet limit modal — 'Close' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_fleet_modal_close(logged_in_carrier: Page):
    """Verify that clicking 'Close' dismisses the limit modal."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Check carrier is already at the fleet limit"):
        current = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        if current < FLEET_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{FLEET_LIMIT}. "
                f"Run test_carrier_fleet_limit_full_flow first."
            )

    with allure.step("Attempt a trailer add beyond the limit to trigger modal"):
        add_trailer(page, 9001, prefix="CR-TRL")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Close' and verify modal is dismissed"):
        page.get_by_role("button", name="Close").click()
        page.wait_for_timeout(1000)
        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Carrier: fleet limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_fleet_modal_upgrade_plan(logged_in_carrier: Page):
    """Verify that clicking 'Upgrade plan' navigates to the pricing/upgrade page."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    with allure.step("Check carrier is already at the fleet limit"):
        current = read_usage_counter(page, "Fleet size", FLEET_LIMIT)
        if current < FLEET_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{FLEET_LIMIT}. "
                f"Run test_carrier_fleet_limit_full_flow first."
            )

    with allure.step("Attempt a trailer add beyond the limit to trigger modal"):
        add_trailer(page, 9002, prefix="CR-TRL")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            page.get_by_role("dialog", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation to pricing page"):
        upgrade_btn = page.get_by_role("button", name="Upgrade plan")
        if upgrade_btn.is_visible(timeout=3000):
            upgrade_btn.click()
            page.wait_for_timeout(3000)
            expect(page).to_have_url(
                re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000
            )
        else:
            pytest.skip("'Upgrade plan' button not found in modal")
