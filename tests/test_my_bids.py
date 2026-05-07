"""
My Bids sahifasi (sent bids) testlari.
/my-bids — user yuborgan bid'lar ro'yxati va status filterlar.

Filter tab'lar: All, Pending, Accepted, Rejected, On the way, Delivered
"""
import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

# My Bids hammaga ochiq (sidebar'da bor)
BID_ROLES = ["broker", "load_owner", "carrier", "owner_operator"]

# Status filter'lar (sahifaning yuqori qismida tab ko'rinadi)
BID_STATUS_FILTERS = ["All", "Pending", "Accepted", "Rejected", "On the way", "Delivered"]


@allure.feature("My Bids")
@allure.story("Page accessible to all roles")
@pytest.mark.parametrize("role", BID_ROLES)
def test_my_bids_page_accessible(request, role: str):
    """/my-bids sahifa ochiladi va URL aynan o'sha bo'lishi kerak."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/my-bids")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    expect(page).to_have_url(f"{APP_URL}/my-bids")


@allure.feature("My Bids")
@allure.story("Status filter tabs visible")
@pytest.mark.parametrize("filter_label", BID_STATUS_FILTERS)
def test_my_bids_filter_tab_visible(logged_in_broker: Page, filter_label: str):
    """Har bir status filter (All/Pending/Accepted/...) sahifada ko'rinishi kerak."""
    page = logged_in_broker
    page.goto(f"{APP_URL}/my-bids")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    expect(page.get_by_text(filter_label, exact=True).first).to_be_visible()


@allure.feature("My Bids")
@allure.story("Clicking a status filter keeps user on the page")
@pytest.mark.parametrize("filter_label", ["Pending", "Accepted", "Rejected", "Delivered"])
def test_my_bids_filter_click_keeps_url(logged_in_broker: Page, filter_label: str):
    """Filter bosilganda URL /my-bids da qoladi (sahifa tark etmaydi)."""
    page = logged_in_broker
    page.goto(f"{APP_URL}/my-bids")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    page.get_by_text(filter_label, exact=True).first.click()
    page.wait_for_timeout(1500)

    expect(page).to_have_url(f"{APP_URL}/my-bids")
