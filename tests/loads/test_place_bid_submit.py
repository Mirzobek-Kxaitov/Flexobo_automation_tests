"""
Place a Bid — form submit testlari (Phase 2).
Har bir test o'z load'ini yaratadi (test isolation).
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from tests.helpers import price_regex
from pages.bid_form_page import BidFormPage

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _open_bid_form(page: Page, price: int) -> BidFormPage:
    page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")
    load_card = page.get_by_text(price_regex(price)).first
    expect(load_card).to_be_visible()
    load_card.click()

    bid = BidFormPage(page)
    bid.open_form()
    return bid


@allure.feature("Place a Bid")
@allure.story("Bid form: empty submit blocks (validation)")
def test_empty_bid_form_blocks_submit(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    bid = _open_bid_form(page, fresh_load_for_bid)

    bid.submit_button.click(force=True)
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}$"))


@allure.feature("Place a Bid")
@allure.story("Bid form: cancel button closes form")
def test_cancel_button_closes_bid_form(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    bid = _open_bid_form(page, fresh_load_for_bid)
    expect(bid.note_input).to_be_visible()
    bid.cancel()


@allure.feature("Place a Bid")
@allure.story("Bid form: note textarea accepts input")
def test_bid_form_note_accepts_input(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    bid = _open_bid_form(page, fresh_load_for_bid)
    bid.fill_note("Test bid from carrier")
    expect(bid.note_input).to_have_value("Test bid from carrier")
