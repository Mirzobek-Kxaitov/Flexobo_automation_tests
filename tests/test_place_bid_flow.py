"""
Place a Bid flow — UI navigation testlari.

Carrier user'i (yuk topib bid yuboradigan) uchun:
1. /loads board ko'rinadi
2. Yukga bosish → /loads/{id} detail sahifa ochiladi
3. Detail sahifada "Place a bid" tugma visible
4. "Place a bid" bosish → bid form same-page'da ochiladi

Har bir test o'z load'ini yaratadi (test isolation).
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _navigate_to_load(page: Page, price: int):
    """Navigate to /loads and click on load with given price."""
    page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")

    thousands = price // 1000
    remainder = price % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")
    load_card = page.get_by_text(price_pattern).first
    expect(load_card).to_be_visible(timeout=20000)
    load_card.click()
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}"), timeout=15000)


@allure.feature("Place a Bid")
@allure.story("Loads board → click load → detail page opens")
def test_clicking_load_opens_detail_page(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _navigate_to_load(page, fresh_load_for_bid)

    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}$"))


@allure.feature("Place a Bid")
@allure.story("Detail page shows Place a bid button")
def test_load_detail_shows_place_a_bid_button(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _navigate_to_load(page, fresh_load_for_bid)

    expect(page.get_by_test_id("bid_place_open_button")).to_be_visible(timeout=10000)


@allure.feature("Place a Bid")
@allure.story("Place a bid button click opens bid form")
def test_clicking_place_a_bid_opens_form(logged_in_carrier: Page, fresh_load_for_bid: int):
    page = logged_in_carrier
    _navigate_to_load(page, fresh_load_for_bid)

    page.get_by_test_id("bid_place_open_button").click()

    expect(page.get_by_test_id("bid_form_container")).to_be_visible()
    expect(page.get_by_test_id("bid_form_note_input")).to_be_visible()
    expect(page.get_by_test_id("bid_form_date_button")).to_be_visible()
    expect(page.get_by_test_id("bid_form_submit_button")).to_be_visible()
