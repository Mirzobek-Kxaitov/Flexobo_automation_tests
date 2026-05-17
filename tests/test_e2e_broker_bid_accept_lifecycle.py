"""
E2E broker bid accept lifecycle: load_owner creates a load, broker places a bid,
load_owner accepts the bid, broker sees it as Accepted in My bids.
"""
import os
import re
import pytest
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import create_load, place_bid_on_load

load_dotenv()
APP_URL = os.getenv("APP_URL")

UNIQUE_PRICE = 14742


@allure.feature("E2E Bid Lifecycle")
@allure.story("Load owner accepts broker bid — broker sees Accepted")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_accepts_broker_bid(
    logged_in_load_owner: Page, logged_in_broker: Page
):
    """
    Multi-user E2E:
    1. Load owner creates a load
    2. Broker places a bid
    3. Load owner accepts the bid from Received bids
    4. Broker sees the bid as Accepted in My bids
    """
    owner = logged_in_load_owner
    broker = logged_in_broker
    owner.set_default_timeout(60000)
    broker.set_default_timeout(60000)

    thousands = UNIQUE_PRICE // 1000
    remainder = UNIQUE_PRICE % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")

    # Step 1: Load owner creates a load
    with allure.step(f"Load owner creates a load with price {UNIQUE_PRICE}"):
        create_load(owner, UNIQUE_PRICE)

    # Step 2: Broker places a bid
    with allure.step("Broker finds the load and places a bid"):
        place_bid_on_load(broker, UNIQUE_PRICE)

    # Step 3: Load owner accepts the bid
    with allure.step("Load owner navigates to Received bids"):
        owner.goto(f"{APP_URL}/profile/root")
        owner.wait_for_timeout(3000)
        owner.get_by_text("Received bids", exact=True).first.click()
        owner.wait_for_timeout(5000)

    with allure.step("Load owner finds the bid card and clicks it"):
        expect(owner.get_by_text(price_pattern).first).to_be_visible(timeout=20000)
        owner.get_by_text(price_pattern).first.click()
        owner.wait_for_timeout(2500)

    with allure.step("Load owner clicks Accept on the broker's bid"):
        bid_card = (
            owner.get_by_role("button")
            .filter(has_text=price_pattern)
            .first
        )
        bid_card.click()
        owner.wait_for_timeout(2000)

        owner.get_by_role("button", name="Accept").click()
        owner.wait_for_timeout(5000)

    # Step 4: Broker verifies bid is Accepted
    with allure.step("Broker navigates to My bids and filters by Accepted"):
        broker.goto(f"{APP_URL}/my-bids")
        broker.wait_for_load_state("domcontentloaded")
        broker.wait_for_timeout(3000)

        broker.get_by_text("Accepted", exact=True).first.click()
        broker.wait_for_timeout(3000)

    with allure.step("Verify the accepted bid is visible"):
        expect(
            broker.get_by_text(price_pattern).first
        ).to_be_visible(timeout=15000)
