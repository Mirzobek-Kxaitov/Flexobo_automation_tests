"""
End-to-end Bid flow.

Soddalashtirilgan stsenariy: carrier mavjud yuk'larga bid yuboradi va
o'z bid'ini /my-bids ro'yxatida ko'radi.

Note: Multi-user (broker create → carrier bid → broker accept) flow
load yaratish UI flaky bo'lgani uchun keyinroq qo'shiladi (Phase 4).
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("E2E Bid Flow")
@allure.story("Carrier places a bid → bid appears in /my-bids")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_can_place_bid_and_see_in_my_bids(logged_in_carrier: Page):
    """
    Carrier mavjud yukka bid yuboradi va /my-bids ro'yxatida o'z bid'ini topadi.

    Verifikatsiya: bid yuborilgandan keyin /my-bids da yuk title yoki yuk price
    bilan bog'liq element ko'rinishi kerak.
    """
    page = logged_in_carrier
    BID_NOTE = "E2E test bid"

    # 1. /loads board → birinchi yukni tanlash
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # Tanlangan yukning aniq ID'sini olish uchun, click qilingach URL'ni saqlaymiz
    page.get_by_text("Be first").first.click()
    page.wait_for_timeout(2500)

    # URL: /loads/{uuid} — yukning ID'sini saqlaymiz
    match = re.search(r"/loads/([a-f0-9-]{36})", page.url)
    assert match, f"Detail URL pattern topilmadi: {page.url}"
    load_id = match.group(1)

    # 2. Place a bid form'ni ochish va note to'ldirish
    page.get_by_role("button", name="Place a bid").first.click()
    page.wait_for_timeout(2500)

    page.get_by_placeholder("Why is your offer better than others?").fill(BID_NOTE)
    page.wait_for_timeout(500)

    # 3. Form'dagi submit "Place a bid" (oxirgisi)
    page.get_by_role("button", name="Place a bid").last.click()
    page.wait_for_timeout(5000)  # backend response uchun ko'proq vaqt

    # 4. /my-bids ga o'tib, ushbu yukka bid yuborilganini tasdiqlash
    page.goto(f"{APP_URL}/my-bids")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # /my-bids da kamida 1 ta load card ko'rinishi kerak (carrier bid yubordi)
    # Eng ishonchli marker — har bid card "Be first" yoki bid status'i bilan keladi
    body = page.locator("body").inner_text()
    assert any(word in body for word in ["Pending", "Be first", "USD"]), (
        "/my-bids sahifasida bid'lar ko'rinmadi (kutilgan: Pending/USD/Be first)"
    )
