"""
E2E simple bid flow — parametrized: actor finds load, places bid,
verifies in /my-bids.

Replaces: test_e2e_bid_flow, test_e2e_broker_bid_flow, test_e2e_oo_bid_flow
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import navigate_to_loads, dismiss_cookie_banner

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("E2E Bid Flow")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("bidder_role", ["carrier", "broker", "owner_operator"])
def test_actor_places_bid_and_sees_in_my_bids(request, bidder_role: str):
    """Actor finds available load, places bid, verifies in /my-bids."""
    page: Page = request.getfixturevalue(f"logged_in_{bidder_role}")
    page.set_default_timeout(60000)

    navigate_to_loads(page)
    dismiss_cookie_banner(page)
    page.locator("div").filter(has_text=re.compile(r"USD.*Fixed rate")).first.click()

    bid_btn = page.get_by_role("button", name="Place a bid").first
    expect(bid_btn).to_be_visible(timeout=10000)
    bid_btn.click()

    note_field = page.get_by_role("textbox", name="Why is your offer better than")
    if note_field.is_visible(timeout=2000):
        note_field.fill(f"E2E {bidder_role} bid")

    page.get_by_role("button", name="Place a bid").last.click()

    limit_modal = page.get_by_text("Limit reached")
    if limit_modal.is_visible(timeout=3000):
        page.get_by_role("button", name="Maybe later").click()
        pytest.skip(f"{bidder_role} bid limit reached")

    page.goto(f"{APP_URL}/my-bids", wait_until="domcontentloaded")
    page.wait_for_function(
        "() => document.body.innerText.trim().length > 50",
        timeout=15000,
    )

    body = page.locator("body").inner_text()
    assert any(word in body for word in ["Pending", "USD", "Active"]), (
        f"No bids found on /my-bids page for {bidder_role}"
    )
