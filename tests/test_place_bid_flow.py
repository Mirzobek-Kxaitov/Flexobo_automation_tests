"""
Place a Bid flow — UI navigation testlari.
Har bir test o'z load'ini yaratadi (test isolation).
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from helpers import price_regex
from pages.bid_form_page import BidFormPage

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _navigate_to_load(page: Page, price: int):
    page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")
    load_card = page.get_by_text(price_regex(price)).first
    expect(load_card).to_be_visible(timeout=20000)
    load_card.click()
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}"), timeout=15000)


@allure.feature("Place a Bid")
@allure.story("Loads board -> click load -> detail page opens")
def test_clicking_load_opens_detail_page(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _navigate_to_load(page, fresh_load_for_bid)
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}$"))


@allure.feature("Place a Bid")
@allure.story("Detail page shows Place a bid button")
def test_load_detail_shows_place_a_bid_button(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _navigate_to_load(page, fresh_load_for_bid)
    expect(BidFormPage(page).open_button).to_be_visible(timeout=10000)


@allure.feature("Place a Bid")
@allure.story("Place a bid button click opens bid form")
def test_clicking_place_a_bid_opens_form(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _navigate_to_load(page, fresh_load_for_bid)
    BidFormPage(page).open_form().expect_form_visible()
