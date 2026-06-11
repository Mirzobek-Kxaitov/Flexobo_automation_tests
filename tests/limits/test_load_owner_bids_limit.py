"""
Load Owner — Bids placed limit enforcement tests.

Scenario:
1. Broker creates a trip, load_owner places a bid (0 -> 3/3)
2. On the 4th bid attempt a "Limit reached" modal appears
3. Modal behavior: "Maybe later" (closes), "Upgrade plan" (navigates)

Multi-user flow:
- broker: creates a trip (with a unique price)
- load_owner: places a bid on that trip

Free plan: Bids placed limit = 3.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.trips_page import TripsPage
from tests.helpers import read_usage_counter, navigate_to_transport, pick_future_date

load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_LIMIT = 3


def _create_trip_and_place_bid(broker: Page, load_owner: Page, price: str) -> None:
    """Broker creates a trip; load_owner finds it by price and places a bid."""
    price_int = int(price)

    with allure.step(f"Broker creates a trip with price {price}"):
        TripsPage(broker).create_trip(
            transport="Trailer 1",
            volume=10,
            loading_city="tashkent",
            loading_suggestion="Tashkent",
            loading_radius=12,
            unloading_city="denov",
            unloading_suggestion="Denov District",
            unloading_radius=12,
            price=price_int,
        )
        broker.wait_for_timeout(3000)

    with allure.step("Load owner navigates to Transport page"):
        navigate_to_transport(load_owner)

    with allure.step(f"Load owner finds the trip card by price {price} and clicks it"):
        thousands = price_int // 1000
        remainder = price_int % 1000
        price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")
        trip_card = load_owner.get_by_text(price_pattern).first
        expect(trip_card).to_be_visible()
        trip_card.click()
        load_owner.wait_for_timeout(1500)

    with allure.step("Load owner opens Place a bid form and submits"):
        load_owner.get_by_role("button", name="Place a bid").first.click()
        load_owner.wait_for_timeout(2000)

        load_owner.get_by_role("button", name="Date").click()
        pick_future_date(load_owner)

        load_owner.get_by_role("textbox", name="Why is your offer better than").fill(
            f"Bids limit test - {price}"
        )
        load_owner.wait_for_timeout(500)

        load_owner.get_by_role("button", name="Place a bid").last.click()
        load_owner.wait_for_timeout(5000)


# ─── Tests ───────────────────────────────────────────────────


@allure.feature("Plan Limits")
@allure.story("Load Owner Free plan: bids placed limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_bids_limit_full_flow(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Verify that after placing 3 bids the 4th attempt shows a 'Limit reached' modal.

    Steps:
    1. Read the current bid count from Usage
    2. Fill up to the limit (broker creates trips, load_owner places bids)
    3. Confirm the counter reached BID_LIMIT
    4. Attempt one more bid and verify the modal appears
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Read current bids placed count from Usage"):
        current = read_usage_counter(owner, "Bids placed", BID_LIMIT)
        needed = max(0, BID_LIMIT - current)

    with allure.step(f"Place {needed} bid(s) to reach the limit"):
        for i in range(needed):
            bid_num = current + i + 1
            price = str(5000 + bid_num)
            with allure.step(f"Placing bid {bid_num}/{BID_LIMIT} with price {price}"):
                _create_trip_and_place_bid(broker, owner, price)

    with allure.step("Confirm counter has reached the limit"):
        final = read_usage_counter(owner, "Bids placed", BID_LIMIT)
        assert final >= BID_LIMIT, (
            f"Expected >= {BID_LIMIT}/{BID_LIMIT}, got {final}/{BID_LIMIT}"
        )

    with allure.step("Attempt one more bid beyond the limit"):
        _create_trip_and_place_bid(broker, owner, str(5000 + BID_LIMIT + 1))

    with allure.step("Verify 'Limit reached' modal is displayed"):
        expect(
            owner.get_by_role("heading", name="Limit reached")
        ).to_be_visible()
        expect(owner.get_by_text("You have reached your limit")).to_be_visible()
        expect(owner.get_by_role("button", name="Upgrade plan")).to_be_visible()
        expect(owner.get_by_role("button", name="Maybe later")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Load Owner: bids limit modal - 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_load_owner_bids_modal_maybe_later(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """Verify that clicking 'Maybe later' closes the limit modal."""
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Check current bids placed count"):
        current = read_usage_counter(owner, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"Load owner is at {current}/{BID_LIMIT}. "
                f"Run test_load_owner_bids_limit_full_flow first."
            )

    with allure.step("Trigger the limit modal with one more bid"):
        _create_trip_and_place_bid(broker, owner, "9001")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            owner.get_by_role("heading", name="Limit reached")
        ).to_be_visible()

    with allure.step("Click 'Maybe later' and verify modal is dismissed"):
        owner.get_by_role("button", name="Maybe later").click()
        owner.wait_for_timeout(1000)
        expect(
            owner.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Load Owner: bids limit modal - 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_load_owner_bids_modal_upgrade_plan(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """Verify that clicking 'Upgrade plan' navigates to the upgrade page."""
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Check current bids placed count"):
        current = read_usage_counter(owner, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"Load owner is at {current}/{BID_LIMIT}. "
                f"Run test_load_owner_bids_limit_full_flow first."
            )

    with allure.step("Trigger the limit modal with one more bid"):
        _create_trip_and_place_bid(broker, owner, "9002")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            owner.get_by_role("heading", name="Limit reached")
        ).to_be_visible()

    with allure.step("Click 'Upgrade plan' and verify navigation to upgrade page"):
        owner.get_by_role("button", name="Upgrade plan").click()
        owner.wait_for_timeout(3000)
        expect(owner).to_have_url(
            re.compile(r".*(pricing|upgrade|plan).*")
        )
