"""
Usage sahifa counterlar testlari — before/after pattern.
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.usage_page import UsagePage

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _place_one_bid(page: Page) -> None:
    page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")

    be_first = page.get_by_text("Be first").first
    expect(be_first).to_be_visible(timeout=20000)
    be_first.click()

    bid_btn = page.get_by_test_id("bid_place_open_button")
    expect(bid_btn).to_be_visible(timeout=10000)
    bid_btn.click()
    expect(page.get_by_test_id("bid_form_container")).to_be_visible(timeout=10000)

    note = page.get_by_test_id("bid_form_note_input")
    if note.is_visible(timeout=2000):
        note.fill("Counter increment test bid")

    page.get_by_test_id("bid_form_submit_button").click()
    page.wait_for_timeout(3000)


@allure.feature("Usage Counter")
@allure.story("Bids placed counter increments by 1 after placing a bid")
@allure.severity(allure.severity_level.CRITICAL)
def test_bids_placed_counter_increments_by_one(free_broker: Page):
    page = free_broker
    page.set_default_timeout(60000)

    usage = UsagePage(page)
    usage.open(APP_URL)
    initial_count = usage.read_counter("usage_bids_placed_card", 20)

    _place_one_bid(page)

    usage.open(APP_URL)
    new_count = usage.read_counter("usage_bids_placed_card", 20)

    assert new_count == initial_count + 1, (
        f"Bids placed counter aniq 1 ga ortishi kerak edi: "
        f"avval={initial_count}, hozir={new_count}, kutilgan={initial_count + 1}"
    )
