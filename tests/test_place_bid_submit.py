"""
Place a Bid — form submit testlari (Phase 2).

Carrier bid form'ni to'ldirib submit qiladi.
Har bir test o'z load'ini yaratadi (test isolation).
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _open_bid_form(page: Page, price: int):
    """Load owner yaratgan loadni topib bid form'ni ochadi."""
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    thousands = price // 1000
    remainder = price % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")
    load_card = page.get_by_text(price_pattern).first
    expect(load_card).to_be_visible(timeout=20000)
    load_card.click()

    bid_btn = page.get_by_test_id("bid_place_open_button")
    expect(bid_btn).to_be_visible(timeout=10000)
    bid_btn.click()
    expect(page.get_by_test_id("bid_form_container")).to_be_visible(timeout=10000)


@allure.feature("Place a Bid")
@allure.story("Bid form: empty submit blocks (validation)")
def test_empty_bid_form_blocks_submit(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _open_bid_form(page, fresh_load_for_bid)

    submit_btn = page.get_by_test_id("bid_form_submit_button")
    submit_btn.click(force=True, timeout=5000)
    page.wait_for_timeout(2000)

    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}$"))


@allure.feature("Place a Bid")
@allure.story("Bid form: cancel button closes form")
def test_cancel_button_closes_bid_form(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _open_bid_form(page, fresh_load_for_bid)

    note_locator = page.get_by_test_id("bid_form_note_input")
    expect(note_locator).to_be_visible()

    page.get_by_test_id("bid_form_cancel_button").click()

    expect(note_locator).not_to_be_visible(timeout=5000)


@allure.feature("Place a Bid")
@allure.story("Bid form: note textarea accepts input")
def test_bid_form_note_accepts_input(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _open_bid_form(page, fresh_load_for_bid)

    note = page.get_by_test_id("bid_form_note_input")
    note.fill("Test bid from carrier")

    expect(note).to_have_value("Test bid from carrier")
