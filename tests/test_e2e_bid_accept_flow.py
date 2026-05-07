"""
E2E Multi-user Bid flow (Phase 4) — 2 ta fixture ishlatadi.

Stsenariy:
1. Load_owner unique-price'li yuk yaratadi
2. Carrier o'sha yukni topib bid yuboradi
3. Load_owner sidebar'dan "Received bids" sahifaga o'tib bid'ni ko'rishi kerak

Texnika: 2 ta fixture (logged_in_load_owner, logged_in_carrier) — har biri
alohida browser context'da, login allaqachon qilingan. Logout/login flow
shart emas — switching by fixture.

Eslatma: load_owner uchun "Received bids" sahifaga to'g'ridan-to'g'ri URL bilan
borib bo'lmaydi (SPA state buziladi) — sidebar linki orqali navigatsiya qilinadi.
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.loads_page import LoadsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("E2E Bid Flow")
@allure.story("Phase 4: load_owner sees carrier's bid")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_sees_carrier_bid_in_received_bids(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """
    Multi-user E2E:
    - load_owner unique price'li yuk yaratadi
    - carrier o'sha yukga bid yuboradi
    - load_owner Received bids sahifada bid'ni ko'radi
    """
    UNIQUE_PRICE = "23579"
    BID_NOTE = "E2E Phase4 bid"
    price_pattern = re.compile(rf"USD\s*{int(UNIQUE_PRICE):,}")

    # ─── 1. LoadOwner: yuk yaratish ────────────────────────────────────
    logged_in_load_owner.set_default_timeout(60000)
    LoadsPage(logged_in_load_owner).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        day="15",
        body_type="Mega truck",
        price=UNIQUE_PRICE,
    )
    # expect_load_created chaqirmaymiz — load_owner ba'zan /profile/root ga ketadi
    logged_in_load_owner.wait_for_timeout(3000)

    # ─── 2. Carrier: yukni topib bid yuborish ──────────────────────────
    logged_in_carrier.set_default_timeout(60000)
    logged_in_carrier.goto(f"{APP_URL}/loads")
    logged_in_carrier.wait_for_timeout(3000)

    # Unique narxli yukni topib bosish
    logged_in_carrier.get_by_text(price_pattern).first.click()
    logged_in_carrier.wait_for_timeout(2500)

    logged_in_carrier.get_by_role("button", name="Place a bid").first.click()
    logged_in_carrier.wait_for_timeout(2500)

    logged_in_carrier.get_by_placeholder("Why is your offer better than others?").fill(BID_NOTE)
    logged_in_carrier.wait_for_timeout(500)

    logged_in_carrier.get_by_role("button", name="Place a bid").last.click()
    logged_in_carrier.wait_for_timeout(5000)

    # ─── 3. LoadOwner: sidebar orqali Received bids sahifaga ────────────
    # Direct URL goto SPA state'ni buzadi — sidebar linki orqali boramiz
    logged_in_load_owner.goto(f"{APP_URL}/profile/root")
    logged_in_load_owner.wait_for_timeout(3000)
    logged_in_load_owner.get_by_text("Received bids", exact=True).first.click()
    logged_in_load_owner.wait_for_timeout(5000)

    # Bid card'da yukning unique narxi ko'rinishi kerak
    expect(
        logged_in_load_owner.get_by_text(price_pattern).first
    ).to_be_visible(timeout=15000)
