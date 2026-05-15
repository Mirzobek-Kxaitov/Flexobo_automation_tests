"""
E2E multi-user bid flow: load_owner creates a load, carrier places a bid,
load_owner verifies the bid in Received bids.
"""
import os
import re
import pytest
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import create_load, navigate_to_loads, pick_future_date

load_dotenv()
APP_URL = os.getenv("APP_URL")

UNIQUE_PRICE = 23579


@allure.feature("E2E Bid Flow")
@allure.story("Load owner sees carrier bid in Received bids")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_sees_carrier_bid_in_received_bids(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """
    Multi-user E2E:
    1. Load owner creates a load with a unique price
    2. Carrier finds the load and places a bid
    3. Load owner navigates to Received bids and verifies the bid is visible
    """
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    thousands = UNIQUE_PRICE // 1000
    remainder = UNIQUE_PRICE % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")

    with allure.step(f"Load owner creates a load with price {UNIQUE_PRICE}"):
        create_load(owner, UNIQUE_PRICE)

    with allure.step("Carrier navigates to loads and finds the load by price"):
        navigate_to_loads(carrier)
        carrier.get_by_text(price_pattern).first.click()
        carrier.wait_for_timeout(2500)

    with allure.step("Carrier places a bid"):
        carrier.get_by_role("button", name="Place a bid").first.click()
        carrier.wait_for_timeout(2000)

        carrier.get_by_role("button", name="Date").click()
        pick_future_date(carrier)

        note_field = carrier.get_by_role("textbox", name="Why is your offer better than")
        if note_field.is_visible(timeout=2000):
            note_field.fill("E2E accept flow bid")
            carrier.wait_for_timeout(500)

        carrier.get_by_role("button", name="Place a bid").last.click()
        carrier.wait_for_timeout(3000)

        # Handle bid limit modal if it appears
        limit_modal = carrier.get_by_text("Limit reached")
        if limit_modal.is_visible(timeout=3000):
            carrier.get_by_role("button", name="Maybe later").click()
            pytest.skip("Carrier daily bid limit reached (3/3) — reset the account or run tomorrow")

    with allure.step("Load owner navigates to Received bids via sidebar"):
        owner.goto(f"{APP_URL}/profile/root")
        owner.wait_for_timeout(3000)
        owner.get_by_text("Received bids", exact=True).first.click()
        owner.wait_for_timeout(5000)

    with allure.step("Verify the bid is visible in Received bids"):
        expect(
            owner.get_by_text(price_pattern).first
        ).to_be_visible(timeout=15000)
