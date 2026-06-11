"""Owner Operator — Bids placed limit enforcement tests.

Scenario:
1. Load owner creates a load, owner_operator places a bid (0 -> 3/3)
2. On the 4th bid attempt the "Limit reached" modal appears
3. Modal behavior: "Maybe later" (closes), "Upgrade plan" (navigates)

Multi-user flow:
- load_owner: creates the load (with a unique price)
- owner_operator: places a bid on that load

Free plan: Bids placed limit = 3.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from tests.helpers import create_load_and_place_bid, read_usage_counter

load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_LIMIT = 3


@allure.feature("Plan Limits")
@allure.story("Owner Operator Free plan: bids placed limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_oo_bids_limit_full_flow(
    logged_in_load_owner: Page, logged_in_owner_operator: Page
):
    """Verify that Owner Operator hits the 'Limit reached' modal on the 4th bid."""
    owner = logged_in_load_owner
    oo = logged_in_owner_operator
    owner.set_default_timeout(60000)
    oo.set_default_timeout(60000)

    with allure.step("Read current bids placed counter"):
        current = read_usage_counter(oo, "Bids placed", BID_LIMIT)
        needed = max(0, BID_LIMIT - current)

    for i in range(needed):
        bid_num = current + i + 1
        price = str(7000 + bid_num)
        with allure.step(f"Place bid #{bid_num}/{BID_LIMIT} (price: {price})"):
            create_load_and_place_bid(owner, oo, price)

    with allure.step(f"Verify counter reached {BID_LIMIT}/{BID_LIMIT}"):
        final = read_usage_counter(oo, "Bids placed", BID_LIMIT)
        assert final >= BID_LIMIT, (
            f"Expected >= {BID_LIMIT}/{BID_LIMIT}, got {final}/{BID_LIMIT}"
        )

    with allure.step("Attempt one more bid to trigger limit modal"):
        create_load_and_place_bid(owner, oo, str(7000 + BID_LIMIT + 1))

    with allure.step("Assert 'Limit reached' modal is visible with correct elements"):
        expect(
            oo.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)
        expect(oo.get_by_text("You have reached your limit")).to_be_visible()
        expect(oo.get_by_role("button", name="Upgrade plan")).to_be_visible()
        expect(oo.get_by_role("button", name="Maybe later")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Owner Operator: bids limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_oo_bids_modal_maybe_later(
    logged_in_load_owner: Page, logged_in_owner_operator: Page
):
    """Verify that clicking 'Maybe later' closes the limit modal."""
    owner = logged_in_load_owner
    oo = logged_in_owner_operator
    owner.set_default_timeout(60000)
    oo.set_default_timeout(60000)

    with allure.step("Check current bids counter — skip if limit not reached"):
        current = read_usage_counter(oo, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"OO is at {current}/{BID_LIMIT}. "
                f"Run test_oo_bids_limit_full_flow first."
            )

    with allure.step("Attempt bid beyond limit to trigger modal"):
        create_load_and_place_bid(owner, oo, "9003")

    with allure.step("Assert 'Limit reached' modal appears"):
        expect(
            oo.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Maybe later' and verify modal closes"):
        oo.get_by_role("button", name="Maybe later").click()
        oo.wait_for_timeout(1000)
        expect(
            oo.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Owner Operator: bids limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_oo_bids_modal_upgrade_plan(
    logged_in_load_owner: Page, logged_in_owner_operator: Page
):
    """Verify that clicking 'Upgrade plan' navigates to the upgrade page."""
    owner = logged_in_load_owner
    oo = logged_in_owner_operator
    owner.set_default_timeout(60000)
    oo.set_default_timeout(60000)

    with allure.step("Check current bids counter — skip if limit not reached"):
        current = read_usage_counter(oo, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"OO is at {current}/{BID_LIMIT}. "
                f"Run test_oo_bids_limit_full_flow first."
            )

    with allure.step("Attempt bid beyond limit to trigger modal"):
        create_load_and_place_bid(owner, oo, "9004")

    with allure.step("Assert 'Limit reached' modal appears"):
        expect(
            oo.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation to upgrade page"):
        oo.get_by_role("button", name="Upgrade plan").click()
        oo.wait_for_timeout(3000)
        expect(oo).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
