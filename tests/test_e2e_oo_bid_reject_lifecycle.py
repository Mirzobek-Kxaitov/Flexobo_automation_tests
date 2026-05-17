"""
E2E OO bid reject lifecycle: load_owner creates a load, owner operator places a bid,
load_owner rejects the bid, owner operator sees it as Rejected in My bids.
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

UNIQUE_PRICE = 17028


@allure.feature("E2E Bid Lifecycle")
@allure.story("Load owner rejects OO bid — OO sees Rejected")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_rejects_oo_bid(
    logged_in_load_owner: Page, logged_in_owner_operator: Page
):
    """
    Multi-user E2E:
    1. Load owner creates a load
    2. Owner Operator places a bid
    3. Load owner rejects the bid from Received bids
    4. Owner Operator sees the bid as Rejected in My bids
    """
    owner = logged_in_load_owner
    oo = logged_in_owner_operator
    owner.set_default_timeout(60000)
    oo.set_default_timeout(60000)

    thousands = UNIQUE_PRICE // 1000
    remainder = UNIQUE_PRICE % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")

    # Step 1: Load owner creates a load
    with allure.step(f"Load owner creates a load with price {UNIQUE_PRICE}"):
        create_load(owner, UNIQUE_PRICE)

    # Step 2: Owner Operator places a bid
    with allure.step("Owner Operator finds the load and places a bid"):
        place_bid_on_load(oo, UNIQUE_PRICE)

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

    with allure.step("Load owner clicks Reject on the OO's bid"):
        bid_card = (
            owner.get_by_role("button")
            .filter(has_text=price_pattern)
            .first
        )
        bid_card.click()
        owner.wait_for_timeout(2000)

        owner.get_by_role("button", name="Reject").click()
        owner.wait_for_timeout(5000)

    # Step 4: Owner Operator verifies bid is Rejected
    with allure.step("Owner Operator navigates to My bids and filters by Rejected"):
        oo.goto(f"{APP_URL}/my-bids")
        oo.wait_for_load_state("domcontentloaded")
        oo.wait_for_timeout(3000)

        oo.get_by_text("Rejected", exact=True).first.click()
        oo.wait_for_timeout(3000)

    with allure.step("Verify the rejected bid is visible"):
        expect(
            oo.get_by_text(price_pattern).first
        ).to_be_visible(timeout=15000)
