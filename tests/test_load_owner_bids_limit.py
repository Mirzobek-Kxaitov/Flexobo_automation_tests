"""
Load Owner — Bids placed limit enforcement testlari.

Stsenariy:
1. Broker trip yaratadi, load_owner bid yuboradi (0 → 3/3)
2. 4-chi bid yuborishda "Limit reached" modal chiqadi
3. Modal behavior: "Maybe later" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Multi-user flow:
- broker: trip yaratadi (unique narx bilan)
- load_owner: o'sha tripga bid yuboradi

Free plan: Bids placed limit = 3.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.trips_page import TripsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_LIMIT = 3


def _pick_future_date(page: Page) -> None:
    """Calendar ochilgandan keyin — next month bosib, birinchi enabled kunni tanlaydi."""
    page.get_by_role("button", name="Next month").click()
    page.wait_for_timeout(300)
    page.locator(
        "td[role='gridcell']:not([data-outside='true']) button:not([disabled])"
    ).first.click()
    page.wait_for_timeout(300)


# ──────────────────── Helper funksiyalar ────────────────────


def _read_bids_placed(page: Page) -> int:
    """Load owner'ning joriy 'Bids placed' qiymatini Usage sahifasidan o'qish."""
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


def _create_trip_and_place_bid(broker: Page, load_owner: Page, price: str) -> None:
    """
    Broker trip yaratadi, load_owner o'sha tripga bid yuboradi.
    """
    price_int = int(price)

    # ─── Broker: trip yaratish ───────────────────────────────
    TripsPage(broker).create_trip(
        transport="Trailer 1",
        volume=10,
        loading_city="tashkent",
        loading_suggestion="Tashkent",
        loading_radius=12,
        unloading_city="denov",
        unloading_suggestion="Denov District",
        unloading_radius=12,
        price=price_int,
    )
    broker.wait_for_timeout(3000)

    # ─── Load owner: Transport sahifasiga o'tish ─────────────────
    transport_nav = load_owner.get_by_role(
        "link", name=re.compile(r"^Transport$|^Транспорт$")
    )
    if transport_nav.is_visible():
        transport_nav.click()
    else:
        load_owner.goto(f"{APP_URL}/transport", wait_until="domcontentloaded")
    load_owner.wait_for_timeout(5000)
    # Blank bo'lsa — reload
    if load_owner.locator("body").inner_text(timeout=3000).strip() == "":
        load_owner.reload(wait_until="domcontentloaded")
        load_owner.wait_for_timeout(5000)

    # Locale-safe pattern: "5,003" (EN) ham "5 003" (RU) ham match bo'ladi
    thousands = price_int // 1000
    remainder = price_int % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")
    trip_card = load_owner.get_by_text(price_pattern).first
    expect(trip_card).to_be_visible(timeout=20000)
    trip_card.click()
    load_owner.wait_for_timeout(1500)

    load_owner.get_by_role("button", name="Place a bid").first.click()
    load_owner.wait_for_timeout(2000)

    # Date — keyingi oydan birinchi enabled kun
    load_owner.get_by_role("button", name="Date").click()
    _pick_future_date(load_owner)

    # Note
    load_owner.get_by_role("textbox", name="Why is your offer better than").fill(
        f"Bids limit test — {price}"
    )
    load_owner.wait_for_timeout(500)

    # Submit
    load_owner.get_by_role("button", name="Place a bid").last.click()
    load_owner.wait_for_timeout(5000)


# ──────────────────── Testlar ────────────────────────────────


@allure.feature("Plan Limits")
@allure.story("Load Owner Free plan: bids placed limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_bids_limit_full_flow(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Load owner 3 ta bid yuborib, 4-chisida 'Limit reached' modal
    chiqishini tekshiradi.

    1. Usage'dan hozirgi bid sonini o'qish
    2. 3 gacha to'ldirish (broker trip yaratadi, load_owner bid yuboradi)
    3. 4-chi bid → modal chiqishi kerak
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    # ─── Hozirgi holatni o'qish ─────────────────────────────
    current = _read_bids_placed(owner)
    needed = max(0, BID_LIMIT - current)
    print(f"\n[BIDS] Hozirgi: {current}/{BID_LIMIT}, kerakli: {needed} ta bid")

    # ─── Limit'gacha to'ldirish ──────────────────────────────
    for i in range(needed):
        bid_num = current + i + 1
        price = str(5000 + bid_num)
        print(f"[BIDS] Bid #{bid_num}/{BID_LIMIT} yuborilmoqda (price: {price})...")
        _create_trip_and_place_bid(broker, owner, price)

    # ─── Limitga yetganini tasdiqlash ────────────────────────
    final = _read_bids_placed(owner)
    assert final >= BID_LIMIT, (
        f"Kutilgan >= {BID_LIMIT}/{BID_LIMIT}, haqiqiy {final}/{BID_LIMIT}"
    )
    print(f"[BIDS] Tasdiqlandi: {final}/{BID_LIMIT}")

    # ─── 4-chi bid: modal chiqishi kerak ─────────────────────
    print("[BIDS] 4-chi bid yuborilmoqda (modal kutilmoqda)...")
    _create_trip_and_place_bid(broker, owner, str(5000 + BID_LIMIT + 1))

    # ─── Modal verifikatsiya ─────────────────────────────────
    expect(
        owner.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    expect(owner.get_by_text("You have reached your limit")).to_be_visible()
    expect(owner.get_by_role("button", name="Upgrade plan")).to_be_visible()
    expect(owner.get_by_role("button", name="Maybe later")).to_be_visible()

    print("[BIDS] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("Load Owner: bids limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_load_owner_bids_modal_maybe_later(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """'Maybe later' bosilganda modal yopilishini tekshiradi."""
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    current = _read_bids_placed(owner)
    if current < BID_LIMIT:
        pytest.skip(
            f"Load owner {current}/{BID_LIMIT} holatda. Avval "
            f"test_load_owner_bids_limit_full_flow ni ishga tushiring."
        )

    _create_trip_and_place_bid(broker, owner, "9001")

    expect(
        owner.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    owner.get_by_role("button", name="Maybe later").click()
    owner.wait_for_timeout(1000)

    expect(
        owner.get_by_role("heading", name="Limit reached")
    ).not_to_be_visible()

    print("[MODAL] ✅ 'Maybe later' bosildi — modal yopildi!")


@allure.feature("Plan Limits")
@allure.story("Load Owner: bids limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_load_owner_bids_modal_upgrade_plan(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """'Upgrade plan' bosilganda upgrade sahifasiga o'tishini tekshiradi."""
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    current = _read_bids_placed(owner)
    if current < BID_LIMIT:
        pytest.skip(
            f"Load owner {current}/{BID_LIMIT} holatda. Avval "
            f"test_load_owner_bids_limit_full_flow ni ishga tushiring."
        )

    _create_trip_and_place_bid(broker, owner, "9002")

    expect(
        owner.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    owner.get_by_role("button", name="Upgrade plan").click()
    owner.wait_for_timeout(3000)

    expect(owner).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)

    print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
