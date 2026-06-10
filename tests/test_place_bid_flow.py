"""
Place a Bid flow — UI navigation testlari.

Carrier user'i (yuk topib bid yuboradigan) uchun:
1. /loads board ko'rinadi
2. Yukga bosish → /loads/{id} detail sahifa ochiladi
3. Detail sahifada "Place a bid" tugma visible
4. "Place a bid" bosish → bid form same-page'da ochiladi

Note: Bid yuborish (form to'ldirib submit) — bu Phase 2, alohida testda.
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("Place a Bid")
@allure.story("Loads board → click load → detail page opens")
def test_clicking_load_opens_detail_page(logged_in_carrier: Page):
    """
    Carrier /loads board'da yuk ustiga bossa, detail sahifa /loads/{uuid}
    ochilishi kerak.
    """
    page = logged_in_carrier
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # Birinchi "Be first" link/element bossa, detail sahifa ochiladi
    page.get_by_text("Be first").first.click()
    page.wait_for_timeout(2500)

    # URL pattern: /loads/{uuid}
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}$"))


@allure.feature("Place a Bid")
@allure.story("Detail page shows Place a bid button")
def test_load_detail_shows_place_a_bid_button(logged_in_carrier: Page):
    """
    Detail sahifada (boshqa user yuki) "Place a bid" tugma visible bo'lishi kerak.
    """
    page = logged_in_carrier
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    page.get_by_text("Be first").first.click()
    page.wait_for_timeout(2500)

    expect(page.get_by_test_id("bid_place_open_button")).to_be_visible(timeout=10000)


@allure.feature("Place a Bid")
@allure.story("Place a bid button click opens bid form")
def test_clicking_place_a_bid_opens_form(logged_in_carrier: Page):
    """
    "Place a bid" tugmani bossak, bid form open bo'lishi kerak.
    Form indikatorlar: "Propose" matni, yoki price input, yoki Submit/Send tugma.
    """
    page = logged_in_carrier
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    page.get_by_text("Be first").first.click()
    page.wait_for_timeout(2500)

    page.get_by_test_id("bid_place_open_button").click()

    expect(page.get_by_test_id("bid_form_container")).to_be_visible()
    expect(page.get_by_test_id("bid_form_note_input")).to_be_visible()
    expect(page.get_by_test_id("bid_form_date_button")).to_be_visible()
    expect(page.get_by_test_id("bid_form_submit_button")).to_be_visible()
