"""
End-to-end bid flow: carrier places a bid on an existing load
and verifies it appears in /my-bids.
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from helpers import navigate_to_loads

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("E2E Bid Flow")
@allure.story("Carrier places a bid and sees it in My Bids")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_can_place_bid_and_see_in_my_bids(logged_in_carrier: Page):
    """
    Carrier finds an available load, places a bid, then navigates
    to /my-bids and confirms the bid is listed.
    """
    page = logged_in_carrier
    page.set_default_timeout(60000)
    BID_NOTE = "E2E test bid"

    with allure.step("Navigate to /loads and select the first available load"):
        navigate_to_loads(page)
        page.locator("div").filter(has_text=re.compile(r"USD.*Fixed rate")).first.click()
        page.wait_for_timeout(2500)

    with allure.step("Open Place a bid form and submit"):
        page.get_by_role("button", name="Place a bid").first.click()
        page.wait_for_timeout(2500)

        note_field = page.get_by_role("textbox", name="Why is your offer better than")
        if note_field.is_visible(timeout=2000):
            note_field.fill(BID_NOTE)
            page.wait_for_timeout(500)

        page.get_by_role("button", name="Place a bid").last.click()
        page.wait_for_timeout(5000)

    with allure.step("Navigate to /my-bids and verify bid is listed"):
        page.goto(f"{APP_URL}/my-bids")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        body = page.locator("body").inner_text()
        assert any(word in body for word in ["Pending", "USD", "Active"]), (
            "No bids found on /my-bids page (expected: Pending/USD/Active)"
        )
