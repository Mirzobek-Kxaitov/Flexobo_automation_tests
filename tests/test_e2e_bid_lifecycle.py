"""
E2E bid lifecycle — parametrized: owner creates load, bidder bids,
owner accepts/rejects, bidder verifies status in My bids.

Replaces: test_e2e_bid_accept_lifecycle, test_e2e_bid_reject_lifecycle,
          test_e2e_broker_bid_accept_lifecycle, test_e2e_broker_bid_reject_lifecycle,
          test_e2e_oo_bid_accept_lifecycle, test_e2e_oo_bid_reject_lifecycle
"""
import os
import re
import random
import pytest
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import create_load, place_bid_on_load

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("E2E Bid Lifecycle")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("bidder_role", ["carrier", "broker", "owner_operator"])
@pytest.mark.parametrize("action,expected_tab", [
    ("Accept", "Accepted"),
    ("Reject", "Rejected"),
])
def test_bid_lifecycle(
    request, logged_in_load_owner: Page,
    bidder_role: str, action: str, expected_tab: str,
):
    """Owner creates load → bidder bids → owner accepts/rejects → bidder sees status."""
    owner = logged_in_load_owner
    bidder: Page = request.getfixturevalue(f"logged_in_{bidder_role}")

    price = random.randint(10000, 49999)
    thousands = price // 1000
    remainder = price % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")

    # 1. Owner creates load
    create_load(owner, price)

    # 2. Bidder places bid
    place_bid_on_load(bidder, price)

    # 3. Owner accepts/rejects
    owner.goto(f"{APP_URL}/profile/root", wait_until="domcontentloaded")
    received = owner.get_by_text("Received bids", exact=True).first
    expect(received).to_be_visible(timeout=10000)
    received.click()

    bid_card = owner.get_by_text(price_pattern).first
    expect(bid_card).to_be_visible(timeout=20000)
    bid_card.click()
    owner.wait_for_timeout(2000)

    owner.get_by_role("button").filter(has_text=price_pattern).first.click()
    owner.wait_for_timeout(1000)

    owner.get_by_role("button", name=action).click()
    owner.wait_for_timeout(3000)

    # 4. Bidder verifies status
    bidder.goto(f"{APP_URL}/my-bids", wait_until="domcontentloaded")
    tab = bidder.get_by_text(expected_tab, exact=True).first
    expect(tab).to_be_visible(timeout=10000)
    tab.click()
    bidder.wait_for_timeout(2000)

    expect(bidder.get_by_text(price_pattern).first).to_be_visible(timeout=15000)
