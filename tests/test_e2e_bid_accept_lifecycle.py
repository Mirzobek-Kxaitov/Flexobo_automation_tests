"""
E2E bid accept lifecycle: load_owner creates a load, carrier places a bid,
load_owner accepts the bid, carrier sees it as Accepted in My bids.
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

UNIQUE_PRICE = 27381


@allure.feature("E2E Bid Lifecycle")
@allure.story("Load owner accepts bid — carrier sees Accepted")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_accepts_bid_and_carrier_sees_accepted(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """
    Multi-user E2E:
    1. Load owner creates a load
    2. Carrier places a bid
    3. Load owner accepts the bid from Received bids
    4. Carrier sees the bid as Accepted in My bids
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

    # Step 2: Carrier places a bid
    with allure.step("Carrier finds the load and places a bid"):
        navigate_to_loads(carrier)
        carrier.get_by_text(price_pattern).first.click()
        carrier.wait_for_timeout(2500)

        carrier.get_by_role("button", name="Place a bid").first.click()
        carrier.wait_for_timeout(2000)

        carrier.get_by_role("button", name="Date").click()
        pick_future_date(carrier)

        note_field = carrier.get_by_role("textbox", name="Why is your offer better than")
        if note_field.is_visible(timeout=2000):
            note_field.fill("E2E lifecycle accept bid")
            carrier.wait_for_timeout(500)

        carrier.get_by_role("button", name="Place a bid").last.click()
        carrier.wait_for_timeout(3000)

        limit_modal = carrier.get_by_text("Limit reached")
        if limit_modal.is_visible(timeout=3000):
            carrier.get_by_role("button", name="Maybe later").click()
            pytest.skip("Carrier daily bid limit reached — reset the account or run tomorrow")

        carrier.wait_for_timeout(2000)

    # Step 3: Load owner accepts the bid
    with allure.step("Load owner navigates to Received bids"):
        owner.goto(f"{APP_URL}/profile/root")
        owner.wait_for_timeout(3000)
        owner.get_by_text("Received bids", exact=True).first.click()
        owner.wait_for_timeout(5000)

    with allure.step("Load owner finds the bid card and clicks it"):
        owner.get_by_text(price_pattern).first.click()
        owner.wait_for_timeout(2500)

    with allure.step("Load owner clicks Accept on the carrier's bid"):
        bid_card = (
            owner.get_by_role("button")
            .filter(has_text=price_pattern)
            .filter(has_text=re.compile(r"carrier", re.IGNORECASE))
            .first
        )
        bid_card.click()
        owner.wait_for_timeout(2000)

        owner.get_by_role("button", name="Accept").click()
        owner.wait_for_timeout(5000)

    # Step 4: Carrier verifies bid is Accepted
    with allure.step("Carrier navigates to My bids and filters by Accepted"):
        carrier.goto(f"{APP_URL}/my-bids")
        carrier.wait_for_load_state("domcontentloaded")
        carrier.wait_for_timeout(3000)

        carrier.get_by_text("Accepted", exact=True).first.click()
        carrier.wait_for_timeout(3000)

    with allure.step("Verify the accepted bid is visible"):
        expect(
            carrier.get_by_text(price_pattern).first
        ).to_be_visible(timeout=15000)
