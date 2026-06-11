"""
Owner Operator — Active transport limit enforcement tests.

Scenario:
1. OO creates 1 trip (0 → 1/1)
2. On the 2nd trip creation attempt, a "Limit reached" modal appears
3. Modal behavior: "Maybe later"/"Close" (dismisses), "Upgrade plan" (navigates)

Free plan: Active transport limit = 1.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from tests.helpers import read_usage_counter
from pages.trips_page import TripsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")

TRANSPORT_LIMIT = 1


def _create_one_trip(page: Page, price: int) -> None:
    """Create a trip for the Owner Operator."""
    TripsPage(page).create_trip(
        transport="Trailer 1",
        volume=10,
        loading_city="tashkent",
        loading_suggestion="Tashkent",
        loading_radius=12,
        unloading_city="denov",
        unloading_suggestion="Denov District",
        unloading_radius=12,
        price=price,
    )
    page.wait_for_timeout(3000)


@pytest.mark.xfail(reason="BUG: Active transport limit not enforced — trips can be created beyond limit")
@allure.feature("Plan Limits")
@allure.story("Owner Operator Free plan: active transport limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_oo_active_transport_limit_full_flow(logged_in_owner_operator: Page):
    """
    Verify that OO sees a 'Limit reached' modal when attempting
    to create a 2nd trip after the active transport limit is reached.
    """
    page = logged_in_owner_operator
    page.set_default_timeout(60000)

    with allure.step("Read current active transport counter"):
        current = read_usage_counter(page, "Active transport", TRANSPORT_LIMIT)
        needed = max(0, TRANSPORT_LIMIT - current)

    with allure.step(f"Fill up to limit: create {needed} trip(s)"):
        for i in range(needed):
            num = current + i + 1
            price = 8000 + num
            with allure.step(f"Create trip #{num}/{TRANSPORT_LIMIT} (price: {price})"):
                _create_one_trip(page, price)

    with allure.step("Confirm counter has reached the limit"):
        final = read_usage_counter(page, "Active transport", TRANSPORT_LIMIT)
        assert final >= TRANSPORT_LIMIT, (
            f"Expected >= {TRANSPORT_LIMIT}/{TRANSPORT_LIMIT}, got {final}/{TRANSPORT_LIMIT}"
        )

    with allure.step("Attempt to create one more trip — expect 'Limit reached' modal"):
        _create_one_trip(page, 8000 + TRANSPORT_LIMIT + 1)

    with allure.step("Assert 'Limit reached' modal is visible"):
        modal_heading = page.get_by_role("heading", name="Limit reached")
        modal_dialog = page.get_by_role("dialog", name="Limit reached")
        expect(modal_heading.or_(modal_dialog)).to_be_visible(timeout=10000)


@pytest.mark.xfail(reason="BUG: Active transport limit not enforced — trips can be created beyond limit")
@allure.feature("Plan Limits")
@allure.story("Owner Operator: active transport modal — dismiss")
@allure.severity(allure.severity_level.NORMAL)
def test_oo_active_transport_modal_dismiss(logged_in_owner_operator: Page):
    """Verify that clicking 'Maybe later' or 'Close' dismisses the limit modal."""
    page = logged_in_owner_operator
    page.set_default_timeout(60000)

    with allure.step("Read current active transport counter"):
        current = read_usage_counter(page, "Active transport", TRANSPORT_LIMIT)
        if current < TRANSPORT_LIMIT:
            pytest.skip(
                f"OO is at {current}/{TRANSPORT_LIMIT}. "
                f"Run test_oo_active_transport_limit_full_flow first."
            )

    with allure.step("Attempt to create a trip beyond the limit"):
        _create_one_trip(page, 9005)

    with allure.step("Assert 'Limit reached' modal is visible"):
        modal_heading = page.get_by_role("heading", name="Limit reached")
        modal_dialog = page.get_by_role("dialog", name="Limit reached")
        expect(modal_heading.or_(modal_dialog)).to_be_visible(timeout=10000)

    with allure.step("Dismiss the modal via 'Maybe later' or 'Close'"):
        maybe_later = page.get_by_role("button", name="Maybe later")
        close_btn = page.get_by_role("button", name="Close")
        if maybe_later.is_visible(timeout=2000):
            maybe_later.click()
        else:
            close_btn.click()
        page.wait_for_timeout(1000)

    with allure.step("Assert modal is no longer visible"):
        expect(modal_heading.or_(modal_dialog)).not_to_be_visible()


@pytest.mark.xfail(reason="BUG: Active transport limit not enforced — trips can be created beyond limit")
@allure.feature("Plan Limits")
@allure.story("Owner Operator: active transport modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_oo_active_transport_modal_upgrade_plan(logged_in_owner_operator: Page):
    """Verify that clicking 'Upgrade plan' in the modal navigates to the upgrade page."""
    page = logged_in_owner_operator
    page.set_default_timeout(60000)

    with allure.step("Read current active transport counter"):
        current = read_usage_counter(page, "Active transport", TRANSPORT_LIMIT)
        if current < TRANSPORT_LIMIT:
            pytest.skip(
                f"OO is at {current}/{TRANSPORT_LIMIT}. "
                f"Run test_oo_active_transport_limit_full_flow first."
            )

    with allure.step("Attempt to create a trip beyond the limit"):
        _create_one_trip(page, 9006)

    with allure.step("Assert 'Limit reached' modal is visible"):
        modal_heading = page.get_by_role("heading", name="Limit reached")
        modal_dialog = page.get_by_role("dialog", name="Limit reached")
        expect(modal_heading.or_(modal_dialog)).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation"):
        upgrade_btn = page.get_by_role("button", name="Upgrade plan")
        if upgrade_btn.is_visible(timeout=3000):
            upgrade_btn.click()
            page.wait_for_timeout(3000)
            expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
        else:
            pytest.skip("'Upgrade plan' button not found in modal")
