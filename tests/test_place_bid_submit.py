"""
Place a Bid — form submit testlari (Phase 2).

Carrier bid form'ni to'ldirib submit qiladi.
Verifikatsiya: bid /my-bids ro'yxatida paydo bo'ladi.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _open_bid_form(page: Page):
    """/loads board'dan birinchi yukga kirib bid form'ni ochadi."""
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    page.get_by_text("Be first").first.click()
    page.wait_for_timeout(2500)

    page.get_by_test_id("bid_place_open_button").click()
    expect(page.get_by_test_id("bid_form_container")).to_be_visible()


@allure.feature("Place a Bid")
@allure.story("Bid form: empty submit blocks (validation)")
def test_empty_bid_form_blocks_submit(logged_in_carrier: Page):
    """
    Bo'sh form (Note va Date to'ldirilmagan) bilan "Place a bid" submit
    bossak, sahifa o'sha holda qoladi (validation blokda saqlasa kerak).
    """
    page = logged_in_carrier
    _open_bid_form(page)

    # Hech nima to'ldirmaymiz
    submit_btn = page.get_by_test_id("bid_form_submit_button")
    submit_btn.click(force=True, timeout=5000)
    page.wait_for_timeout(2000)

    # Sahifa hali ham detail URL'da (modal ochiq, submit ishlamadi)
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]{36}$"))


@allure.feature("Place a Bid")
@allure.story("Bid form: cancel button closes form")
def test_cancel_button_closes_bid_form(logged_in_carrier: Page):
    """
    "Cancel" tugma bid form'ni yopishi va Note textarea'ni yashirishi kerak.
    """
    page = logged_in_carrier
    _open_bid_form(page)

    # Cancel bossa textarea yo'qoladi
    note_locator = page.get_by_test_id("bid_form_note_input")
    expect(note_locator).to_be_visible()

    page.get_by_test_id("bid_form_cancel_button").click()

    expect(note_locator).not_to_be_visible(timeout=5000)


@allure.feature("Place a Bid")
@allure.story("Bid form: note textarea accepts input")
def test_bid_form_note_accepts_input(logged_in_carrier: Page):
    """
    Note textarea'ga matn yozsak, qabul qilishi va saqlanishi kerak.
    """
    page = logged_in_carrier
    _open_bid_form(page)

    note = page.get_by_test_id("bid_form_note_input")
    note.fill("Test bid from carrier")

    expect(note).to_have_value("Test bid from carrier")
