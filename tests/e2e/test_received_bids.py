"""
Received Bids sahifasi (kelgan bid'lar) testlari.
/received-bids — user'ning yuklariga kelgan bid'lar ro'yxati.

Note: filter tab'lar (Pending/Accepted/...) faqat received bid'lar bo'lganda
ko'rinadi (mock env'da broker'da received bid yo'q). Shuning uchun bu
testlar faqat sahifa accessibility'ni tekshiradi.
"""
import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_ROLES = ["broker", "load_owner", "carrier", "owner_operator"]


@allure.feature("Received Bids")
@allure.story("Page accessible to all roles")
@pytest.mark.parametrize("role", BID_ROLES)
def test_received_bids_page_accessible(request, role: str):
    """/received-bids sahifa ochiladi va URL aynan o'sha bo'lishi kerak."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/received-bids")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    expect(page).to_have_url(f"{APP_URL}/received-bids")
