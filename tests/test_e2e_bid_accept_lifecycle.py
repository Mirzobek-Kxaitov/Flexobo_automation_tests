"""
E2E Multi-user Bid Accept Lifecycle (Phase 5) — bid lifecycle davomi.

Stsenariy:
1. Load_owner unique-price'li yuk yaratadi
2. Carrier bid yuboradi
3. Load_owner Received bids → o'sha bid'ni Accept qiladi
4. Verifikatsiya: carrier /my-bids/Accepted filterda bid'ini ko'radi

Texnika: 2 ta fixture (alohida browser context'da). Sidebar navigation
ishlatiladi (direct goto SPA state'ni buzadi).
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.loads_page import LoadsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("E2E Bid Lifecycle")
@allure.story("Phase 5: load_owner accepts carrier's bid → carrier sees Accepted")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_accepts_bid_and_carrier_sees_accepted(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """
    Multi-user E2E:
    - load_owner yuk yaratadi
    - carrier bid yuboradi
    - load_owner bid'ni Accept qiladi
    - carrier /my-bids/Accepted da bid'ni ko'radi
    """
    UNIQUE_PRICE = "27381"  # test_e2e_bid_accept_flow.py "23579" dan farq qilsin
    BID_NOTE = "E2E Lifecycle Accept bid"
    price_pattern = re.compile(rf"USD\s*{int(UNIQUE_PRICE):,}")

    # ─── 1. Load_owner: yuk yaratish ────────────────────────────────────
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
    logged_in_load_owner.wait_for_timeout(3000)

    # ─── 2. Carrier: bid yuborish ───────────────────────────────────────
    logged_in_carrier.set_default_timeout(60000)
    logged_in_carrier.goto(f"{APP_URL}/loads")
    logged_in_carrier.wait_for_timeout(3000)

    logged_in_carrier.get_by_text(price_pattern).first.click()
    logged_in_carrier.wait_for_timeout(2500)

    logged_in_carrier.get_by_role("button", name="Place a bid").first.click()
    logged_in_carrier.wait_for_timeout(2500)

    logged_in_carrier.get_by_placeholder("Why is your offer better than others?").fill(BID_NOTE)
    logged_in_carrier.wait_for_timeout(500)

    logged_in_carrier.get_by_role("button", name="Place a bid").last.click()
    logged_in_carrier.wait_for_timeout(5000)

    # ─── 3. Load_owner: Received bids → bid'ni Accept qilish ───────────
    logged_in_load_owner.goto(f"{APP_URL}/profile/root")
    logged_in_load_owner.wait_for_timeout(3000)
    logged_in_load_owner.get_by_text("Received bids", exact=True).first.click()
    logged_in_load_owner.wait_for_timeout(5000)

    # Yuk kartochkasini topib bosish (UNIQUE_PRICE bo'yicha — kengaytiriladi)
    logged_in_load_owner.get_by_text(price_pattern).first.click()
    logged_in_load_owner.wait_for_timeout(2500)

    # Carrier bid kartochkasini topish: button + price + "carrier" matni
    # (codegen ko'rsatdi: bid button name'da "USD <amount>" va role nomi bor)
    bid_button = (
        logged_in_load_owner.get_by_role("button")
        .filter(has_text=price_pattern)
        .filter(has_text=re.compile(r"carrier", re.IGNORECASE))
        .first
    )
    bid_button.click()
    logged_in_load_owner.wait_for_timeout(2000)

    # Accept tugmasini bosish
    logged_in_load_owner.get_by_role("button", name="Accept").click()
    logged_in_load_owner.wait_for_timeout(5000)

    # ─── 4. Carrier: /my-bids/Accepted da bid'ni ko'rish ───────────────
    logged_in_carrier.goto(f"{APP_URL}/my-bids")
    logged_in_carrier.wait_for_load_state("domcontentloaded")
    logged_in_carrier.wait_for_timeout(3000)

    # "Accepted" filter tab
    logged_in_carrier.get_by_text("Accepted", exact=True).first.click()
    logged_in_carrier.wait_for_timeout(3000)

    # Accepted ro'yxatda bizning yuk (UNIQUE_PRICE) ko'rinishi kerak
    expect(
        logged_in_carrier.get_by_text(price_pattern).first
    ).to_be_visible(timeout=15000)
