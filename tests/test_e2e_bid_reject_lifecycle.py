"""
E2E bid reject lifecycle: load_owner creates a load, carrier places a bid,
load_owner rejects the bid, carrier sees it as Rejected in My bids.
"""
import os
import re
import pytest
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import create_load, navigate_to_loads, pick_future_date, place_bid_on_load

load_dotenv()
APP_URL = os.getenv("APP_URL")

UNIQUE_PRICE = 19264


@allure.feature("E2E Bid Lifecycle")
@allure.story("Load owner rejects bid — carrier sees Rejected")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_rejects_bid_and_carrier_sees_rejected(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """
    Multi-user E2E:
    1. Load owner creates a load
    2. Carrier places a bid
    3. Load owner rejects the bid from Received bids
    4. Carrier sees the bid as Rejected in My bids
    """
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    thousands = UNIQUE_PRICE // 1000
    remainder = UNIQUE_PRICE % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")

    # Step 1: Load owner creates a load
    with allure.step(f"Load owner creates a load with price {UNIQUE_PRICE}"):
        create_load(owner, UNIQUE_PRICE)

    # Step 2: Carrier places a bid (skips if daily limit reached)
    with allure.step("Carrier finds the load and places a bid"):
        place_bid_on_load(carrier, UNIQUE_PRICE)

    # Step 3: Load owner rejects the bid
    with allure.step("Load owner navigates to Received bids"):
        owner.goto(f"{APP_URL}/profile/root")
        owner.wait_for_timeout(3000)
        owner.get_by_text("Received bids", exact=True).first.click()
        owner.wait_for_timeout(5000)

    with allure.step("Load owner finds the bid card and clicks it"):
        expect(owner.get_by_text(price_pattern).first).to_be_visible(timeout=20000)
        owner.get_by_text(price_pattern).first.click()
        owner.wait_for_timeout(2500)

    with allure.step("Load owner clicks Reject on the carrier's bid"):
        bid_card = (
            owner.get_by_role("button")
            .filter(has_text=price_pattern)
            .filter(has_text=re.compile(r"carrier", re.IGNORECASE))
            .first
        )
        bid_card.click()
        owner.wait_for_timeout(2000)

        owner.get_by_role("button", name="Reject").click()
        owner.wait_for_timeout(5000)

    # Step 4: Carrier verifies bid is Rejected
    with allure.step("Carrier navigates to My bids and filters by Rejected"):
        carrier.goto(f"{APP_URL}/my-bids")
        carrier.wait_for_load_state("domcontentloaded")
        carrier.wait_for_timeout(3000)

        carrier.get_by_text("Rejected", exact=True).first.click()
        carrier.wait_for_timeout(3000)

    with allure.step("Verify the rejected bid is visible"):
        expect(
            carrier.get_by_text(price_pattern).first
        ).to_be_visible(timeout=15000)
