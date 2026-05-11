"""
Carrier — Bids placed limit enforcement tests.

Scenario:
1. Load owner creates a load, carrier places a bid (0 → 3/3).
2. On the 4th bid attempt a 'Limit reached' modal appears.
3. Modal behaviour: 'Maybe later' closes it, 'Upgrade plan' navigates away.

Multi-user flow:
- load_owner: creates a load (with a unique price).
- carrier: places a bid on that load via the Loads page.

Free plan: Bids placed limit = 3.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import create_load_and_place_bid, read_usage_counter

load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_LIMIT = 3


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: bids placed limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_bids_limit_full_flow(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """
    Verify that the carrier cannot place more than BID_LIMIT bids on the
    free plan and that a 'Limit reached' modal is shown on the (BID_LIMIT+1)th
    attempt.

    Steps:
    1. Read the current bids counter from the Usage tab.
    2. Fill up to the limit (load_owner creates loads, carrier bids on them).
    3. Confirm the counter reached the limit.
    4. Attempt one more bid and verify the modal.
    """
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    with allure.step("Read current bids counter from Usage tab"):
        current = read_usage_counter(carrier, "Bids placed", BID_LIMIT)
        needed = max(0, BID_LIMIT - current)

    with allure.step(f"Fill bids up to limit (current={current}, needed={needed})"):
        for i in range(needed):
            bid_num = current + i + 1
            price = str(6000 + bid_num)
            with allure.step(f"Place bid #{bid_num}/{BID_LIMIT} (price={price})"):
                create_load_and_place_bid(owner, carrier, price)

    with allure.step("Confirm bids counter reached the limit"):
        final = read_usage_counter(carrier, "Bids placed", BID_LIMIT)
        assert final >= BID_LIMIT, (
            f"Expected >= {BID_LIMIT}/{BID_LIMIT}, got {final}/{BID_LIMIT}"
        )

    with allure.step("Attempt one more bid beyond the limit"):
        create_load_and_place_bid(owner, carrier, str(6000 + BID_LIMIT + 1))

    with allure.step("Verify 'Limit reached' modal is displayed"):
        expect(
            carrier.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)
        expect(carrier.get_by_text("You have reached your limit")).to_be_visible()
        expect(carrier.get_by_role("button", name="Upgrade plan")).to_be_visible()
        expect(carrier.get_by_role("button", name="Maybe later")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Carrier: bids limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_bids_modal_maybe_later(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """Verify that clicking 'Maybe later' closes the limit modal."""
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    with allure.step("Check carrier is already at the bid limit"):
        current = read_usage_counter(carrier, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{BID_LIMIT}. "
                f"Run test_carrier_bids_limit_full_flow first."
            )

    with allure.step("Attempt a bid beyond the limit to trigger modal"):
        create_load_and_place_bid(owner, carrier, "9001")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            carrier.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Maybe later' and verify modal is dismissed"):
        carrier.get_by_role("button", name="Maybe later").click()
        carrier.wait_for_timeout(1000)
        expect(
            carrier.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Carrier: bids limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_bids_modal_upgrade_plan(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """Verify that clicking 'Upgrade plan' navigates to the pricing/upgrade page."""
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    with allure.step("Check carrier is already at the bid limit"):
        current = read_usage_counter(carrier, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"Carrier is at {current}/{BID_LIMIT}. "
                f"Run test_carrier_bids_limit_full_flow first."
            )

    with allure.step("Attempt a bid beyond the limit to trigger modal"):
        create_load_and_place_bid(owner, carrier, "9002")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            carrier.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation to pricing page"):
        carrier.get_by_role("button", name="Upgrade plan").click()
        carrier.wait_for_timeout(3000)
        expect(carrier).to_have_url(
            re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000
        )
