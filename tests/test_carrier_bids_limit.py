"""
Carrier — Bids placed limit enforcement testlari.

Stsenariy:
1. Load owner load yaratadi, carrier bid yuboradi (0 → 3/3)
2. 4-chi bid yuborishda "Limit reached" modal chiqadi
3. Modal behavior: "Maybe later" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Multi-user flow:
- load_owner: load yaratadi (unique narx bilan)
- carrier: o'sha loadga "Load" sahifasida bid yuboradi

Free plan: Bids placed limit = 3.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv


load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_LIMIT = 3


def _pick_future_date(page: Page) -> None:
    """Calendar ochilgandan keyin — next month bosib, birinchi enabled kunni tanlaydi."""
    page.get_by_role("button", name="Next month").click()
    page.wait_for_timeout(300)
    # Birinchi enabled kun (disabled emas)
    page.locator(
        "td[role='gridcell']:not([data-outside='true']) button:not([disabled])"
    ).first.click()
    page.wait_for_timeout(300)


# ──────────────────── Helper funksiyalar ────────────────────


def _read_bids_placed(page: Page) -> int:
    """Carrier'ning joriy 'Bids placed' qiymatini Usage sahifasidan o'qish."""
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


def _create_load_and_place_bid(load_owner: Page, carrier: Page, price: str) -> None:
    """
    Load owner load yaratadi, carrier o'sha loadga bid yuboradi.
    """
    price_int = int(price)

    # ─── Load owner: load yaratish (codegen asosida) ─────────
    load_owner.get_by_role("button", name="Add").click()
    load_owner.get_by_role("menuitem", name="Load").click()
    load_owner.wait_for_timeout(1000)

    # From
    load_owner.get_by_role("textbox", name="From").fill("TASH")
    load_owner.get_by_text("Tashkent", exact=True).click()

    # To
    load_owner.get_by_role("textbox", name="To").fill("DENA")
    load_owner.get_by_text("Denain", exact=True).click()

    # Load type
    load_owner.get_by_text("Load type", exact=True).click()
    load_owner.get_by_role("option", name="dovcha").click()

    # Date — keyingi oydan birinchi enabled kun
    load_owner.get_by_role("button", name="Date").click()
    _pick_future_date(load_owner)

    # Cookie banner dismiss
    cookie_btn = load_owner.get_by_role("button", name="Accept")
    if cookie_btn.is_visible(timeout=1000):
        cookie_btn.click(force=True)
        load_owner.wait_for_timeout(500)

    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    # Weight
    load_owner.get_by_role("textbox", name="Load weight").fill("12")
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    # Transport type
    load_owner.get_by_role("combobox").filter(has_text="Transport type").click()
    load_owner.get_by_role("option", name="Mega truck").click()
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    # Price
    load_owner.get_by_role("textbox", name="Price").fill(str(price_int))
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    load_owner.get_by_role("button", name="Publish").click()
    load_owner.wait_for_timeout(3000)

    # ─── Carrier: Load sahifasiga o'tish ─────────────────────
    # /profile/root dan keyin React Router orqali navigation qilamiz
    # Agar sahifada nav link ko'rinmasa — oldin bosh sahifaga o'tamiz
    load_nav = carrier.get_by_role(
        "link", name=re.compile(r"^Load$|^Груз$")
    )
    if not load_nav.is_visible():
        carrier.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")
        carrier.wait_for_function(
            "() => document.body.innerText.trim().length > 50",
            timeout=15000,
        )
    else:
        load_nav.click()
        carrier.wait_for_function(
            "() => document.body.innerText.trim().length > 50",
            timeout=15000,
        )

    # Locale-safe pattern: "6,001" (EN) ham "6 001" (RU) ham match bo'ladi
    thousands = price_int // 1000
    remainder = price_int % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")
    load_card = carrier.get_by_text(price_pattern).first
    expect(load_card).to_be_visible(timeout=20000)
    load_card.click()
    carrier.wait_for_timeout(1500)

    carrier.get_by_role("button", name="Place a bid").first.click()
    carrier.wait_for_timeout(2000)

    # Date — keyingi oydan birinchi enabled kun
    carrier.get_by_role("button", name="Date").click()
    _pick_future_date(carrier)

    # Submit
    carrier.get_by_role("button", name="Place a bid").last.click()
    carrier.wait_for_timeout(5000)


# ──────────────────── Testlar ────────────────────────────────


@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: bids placed limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_bids_limit_full_flow(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """
    Carrier 3 ta bid yuborib, 4-chisida 'Limit reached' modal
    chiqishini tekshiradi.

    1. Usage'dan hozirgi bid sonini o'qish
    2. 3 gacha to'ldirish (load_owner load yaratadi, carrier bid yuboradi)
    3. 4-chi bid → modal chiqishi kerak
    """
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    # ─── Hozirgi holatni o'qish ─────────────────────────────
    current = _read_bids_placed(carrier)
    needed = max(0, BID_LIMIT - current)
    print(f"\n[BIDS] Hozirgi: {current}/{BID_LIMIT}, kerakli: {needed} ta bid")

    # ─── Limit'gacha to'ldirish ──────────────────────────────
    for i in range(needed):
        bid_num = current + i + 1
        price = str(6000 + bid_num)
        print(f"[BIDS] Bid #{bid_num}/{BID_LIMIT} yuborilmoqda (price: {price})...")
        _create_load_and_place_bid(owner, carrier, price)

    # ─── Limitga yetganini tasdiqlash ────────────────────────
    final = _read_bids_placed(carrier)
    assert final >= BID_LIMIT, (
        f"Kutilgan >= {BID_LIMIT}/{BID_LIMIT}, haqiqiy {final}/{BID_LIMIT}"
    )
    print(f"[BIDS] Tasdiqlandi: {final}/{BID_LIMIT}")

    # ─── 4-chi bid: modal chiqishi kerak ─────────────────────
    print("[BIDS] 4-chi bid yuborilmoqda (modal kutilmoqda)...")
    _create_load_and_place_bid(owner, carrier, str(6000 + BID_LIMIT + 1))

    # ─── Modal verifikatsiya ─────────────────────────────────
    expect(
        carrier.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    expect(carrier.get_by_text("You have reached your limit")).to_be_visible()
    expect(carrier.get_by_role("button", name="Upgrade plan")).to_be_visible()
    expect(carrier.get_by_role("button", name="Maybe later")).to_be_visible()

    print("[BIDS] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("Carrier: bids limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_bids_modal_maybe_later(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """'Maybe later' bosilganda modal yopilishini tekshiradi."""
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    current = _read_bids_placed(carrier)
    if current < BID_LIMIT:
        pytest.skip(
            f"Carrier {current}/{BID_LIMIT} holatda. Avval "
            f"test_carrier_bids_limit_full_flow ni ishga tushiring."
        )

    _create_load_and_place_bid(owner, carrier, "9001")

    expect(
        carrier.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    carrier.get_by_role("button", name="Maybe later").click()
    carrier.wait_for_timeout(1000)

    expect(
        carrier.get_by_role("heading", name="Limit reached")
    ).not_to_be_visible()

    print("[MODAL] ✅ 'Maybe later' bosildi — modal yopildi!")


@allure.feature("Plan Limits")
@allure.story("Carrier: bids limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_bids_modal_upgrade_plan(
    logged_in_load_owner: Page, logged_in_carrier: Page
):
    """'Upgrade plan' bosilganda upgrade sahifasiga o'tishini tekshiradi."""
    owner = logged_in_load_owner
    carrier = logged_in_carrier
    owner.set_default_timeout(60000)
    carrier.set_default_timeout(60000)

    current = _read_bids_placed(carrier)
    if current < BID_LIMIT:
        pytest.skip(
            f"Carrier {current}/{BID_LIMIT} holatda. Avval "
            f"test_carrier_bids_limit_full_flow ni ishga tushiring."
        )

    _create_load_and_place_bid(owner, carrier, "9002")

    expect(
        carrier.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    carrier.get_by_role("button", name="Upgrade plan").click()
    carrier.wait_for_timeout(3000)

    expect(carrier).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)

    print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
