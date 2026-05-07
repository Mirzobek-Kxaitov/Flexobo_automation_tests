"""
Bid limit enforcement testlari — Free plan'dagi cheklov amalda ishlashini
tasdiqlash.

Stsenariy:
1. Broker'ni 20/20 bid limitiga yetkazish (load_owner yuk yaratadi, broker bid yuboradi)
2. 21-chi bid yuborishga harakat → "Limit reached" modal chiqadi
3. Modal behavior: "Maybe later" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Pre-condition: load_owner da yetarli yuk yaratish imkoni bo'lishi kerak.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.loads_page import LoadsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_LIMIT = 20


# ──────────────────── Helper funksiyalar ────────────────────


def _read_bids_placed(page: Page) -> int:
    """Joriy 'Bids placed' qiymatini Usage sahifasidan o'qish."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    card = (
        page.locator("div")
        .filter(has_text="Bids placed")
        .filter(has_text=f"/ {BID_LIMIT}")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(rf"(\d+)\s*/\s*{BID_LIMIT}", text)
    assert match, f"'Bids placed' formatida son topilmadi:\n{text}"
    return int(match.group(1))


def _create_load_and_get_price(load_owner_page: Page, index: int) -> str:
    """Load_owner yangi yuk yaratadi va uning unique narxini qaytaradi."""
    price = str(10000 + index)  # 10001, 10002, ... — har biri unique
    LoadsPage(load_owner_page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        day="15",
        body_type="Mega truck",
        price=price,
    )
    load_owner_page.wait_for_timeout(3000)
    return price


def _place_bid_on_load(broker_page: Page, price: str, note: str) -> None:
    """Broker berilgan narxli yukni topib, bid yuboradi."""
    price_pattern = re.compile(rf"USD\s*{int(price):,}")

    broker_page.goto(f"{APP_URL}/loads")
    broker_page.wait_for_load_state("domcontentloaded")
    broker_page.wait_for_timeout(3500)

    broker_page.get_by_text(price_pattern).first.click()
    broker_page.wait_for_timeout(2500)

    broker_page.get_by_role("button", name="Place a bid").first.click()
    broker_page.wait_for_timeout(2500)

    broker_page.get_by_placeholder("Why is your offer better than others?").fill(note)
    broker_page.wait_for_timeout(500)

    broker_page.get_by_role("button", name="Place a bid").last.click()
    broker_page.wait_for_timeout(5000)


# ──────────────────── Testlar ────────────────────────────────


@allure.feature("Plan Limits")
@allure.story("Free plan: fill to limit and verify 'Limit reached' modal")
@allure.severity(allure.severity_level.CRITICAL)
def test_bid_limit_full_flow(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Broker'ni 20/20 ga yetkazib, 21-chi bidda 'Limit reached' modal
    chiqishini tekshiradi.

    1. Usage'dan hozirgi bid sonini o'qish
    2. Yetishmagan miqdorcha yuk yaratib, bid yuborish
    3. 21-chi bid → modal chiqishi kerak
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    # ─── Hozirgi holatni o'qish ─────────────────────────────
    current = _read_bids_placed(broker)
    needed = BID_LIMIT - current
    print(f"\n[BID LIMIT] Hozirgi: {current}/{BID_LIMIT}, kerakli: {needed} ta bid")

    # ─── Limit'gacha to'ldirish ──────────────────────────────
    for i in range(needed):
        bid_num = current + i + 1
        print(f"[BID LIMIT] Bid #{bid_num}/{BID_LIMIT} yuborilmoqda...")

        price = _create_load_and_get_price(owner, bid_num)
        _place_bid_on_load(broker, price, f"Fill bid #{bid_num}")

    # ─── Limitga yetganini tasdiqlash ────────────────────────
    final = _read_bids_placed(broker)
    assert final == BID_LIMIT, (
        f"Kutilgan {BID_LIMIT}/{BID_LIMIT}, haqiqiy {final}/{BID_LIMIT}"
    )
    print(f"[BID LIMIT] Tasdiqlandi: {final}/{BID_LIMIT}")

    # ─── 21-chi bid: modal chiqishi kerak ────────────────────
    print("[BID LIMIT] 21-chi bid yuborilmoqda (modal kutilmoqda)...")
    extra_price = _create_load_and_get_price(owner, BID_LIMIT + 1)
    _place_bid_on_load(broker, extra_price, "Over limit bid")

    # ─── Modal verifikatsiya ─────────────────────────────────
    expect(
        broker.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    expect(
        broker.get_by_text("You have reached your limit")
    ).to_be_visible()

    expect(
        broker.get_by_role("button", name="Upgrade plan")
    ).to_be_visible()

    expect(
        broker.get_by_role("button", name="Maybe later")
    ).to_be_visible()

    print("[BID LIMIT] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("'Limit reached' modal: 'Maybe later' dismisses modal")
@allure.severity(allure.severity_level.NORMAL)
def test_limit_modal_maybe_later(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Broker limit'da bo'lganda bid yuborib, modal'dagi 'Maybe later'
    bosilganda modal yopilishini tekshiradi.

    Pre-condition: broker 20/20 bo'lishi kerak.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    current = _read_bids_placed(broker)
    if current < BID_LIMIT:
        pytest.skip(
            f"Broker {current}/{BID_LIMIT} holatda. Avval test_bid_limit_full_flow "
            f"ni ishga tushiring."
        )

    # Yangi yuk yaratib, bid yuborish → modal chiqadi
    price = _create_load_and_get_price(owner, 9001)
    _place_bid_on_load(broker, price, "Maybe later test")

    # Modal ko'ringanini tasdiqlash
    expect(
        broker.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    # "Maybe later" bosish
    broker.get_by_role("button", name="Maybe later").click()
    broker.wait_for_timeout(1000)

    # Modal yopilganini tasdiqlash
    expect(
        broker.get_by_role("heading", name="Limit reached")
    ).not_to_be_visible()

    print("[MODAL] ✅ 'Maybe later' bosildi — modal yopildi!")


@allure.feature("Plan Limits")
@allure.story("'Limit reached' modal: 'Upgrade plan' navigates to upgrade page")
@allure.severity(allure.severity_level.NORMAL)
def test_limit_modal_upgrade_plan(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Broker limit'da bo'lganda bid yuborib, modal'dagi 'Upgrade plan'
    bosilganda upgrade sahifasiga o'tishini tekshiradi.

    Pre-condition: broker 20/20 bo'lishi kerak.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    current = _read_bids_placed(broker)
    if current < BID_LIMIT:
        pytest.skip(
            f"Broker {current}/{BID_LIMIT} holatda. Avval test_bid_limit_full_flow "
            f"ni ishga tushiring."
        )

    # Yangi yuk yaratib, bid yuborish → modal chiqadi
    price = _create_load_and_get_price(owner, 9002)
    _place_bid_on_load(broker, price, "Upgrade plan test")

    # Modal ko'ringanini tasdiqlash
    expect(
        broker.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    # "Upgrade plan" bosish
    broker.get_by_role("button", name="Upgrade plan").click()
    broker.wait_for_timeout(3000)

    # URL'da pricing/upgrade bo'lishi kerak
    expect(broker).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)

    print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
