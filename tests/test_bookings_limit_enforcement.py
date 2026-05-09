"""
Bookings limit enforcement testlari — Free plan'dagi cheklov.

Stsenariy:
1. Broker 5 ta booking yaratadi (0 → 5/5)
2. 6-chi bookingda "Limit reached" modal chiqadi
3. Modal behavior: "Maybe later" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Multi-user flow:
- load_owner: yuk yaratadi, broker bid'ni accept qiladi
- broker: bid yuboradi (booking broker'nikiga hisoblanadi)

Sabab (backend): booking.created eventida customerId = bidderId (broker),
shuning uchun broker'ning Bookings counter'i ortadi.

Free plan: Bookings limit = 5.
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

BOOKINGS_LIMIT = 5


# ──────────────────── Helper funksiyalar ────────────────────


def _read_bookings_count(page: Page) -> int:
    """Broker'ning joriy 'Bookings' qiymatini Usage sahifasidan o'qish."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    card = (
        page.locator("div")
        .filter(has_text="Bookings")
        .filter(has_text=f"/ {BOOKINGS_LIMIT}")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(rf"(\d+)\s*/\s*{BOOKINGS_LIMIT}", text)
    assert match, f"'Bookings' formatida son topilmadi:\n{text}"
    return int(match.group(1))


def _create_booking(load_owner: Page, broker: Page, price: str) -> None:
    """
    1 ta booking yaratadi:
    - load_owner yuk yaratadi
    - broker bid yuboradi
    - load_owner bid'ni accept qiladi
    → broker'ning Bookings counter'i +1 bo'ladi
    """
    price_pattern = re.compile(rf"USD\s*{int(price):,}")

    # ─── load_owner: yuk yaratish ───────────────────────────
    LoadsPage(load_owner).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Apple production",
        weight="20",
        day="20",
        body_type="'/40' extendable semi-trailer",
        price=price,
        loading_type="Hydraulic",
        unloading_type="Pneumatic",
    )
    load_owner.wait_for_timeout(3000)

    # ─── broker: yukni topib bid yuborish ───────────────────
    broker.goto(f"{APP_URL}/loads")
    broker.wait_for_load_state("domcontentloaded")
    broker.wait_for_timeout(3500)

    broker.get_by_text(price_pattern).first.click()
    broker.wait_for_timeout(2500)

    broker.get_by_role("button", name="Place a bid").first.click()
    broker.wait_for_timeout(2500)

    broker.get_by_placeholder("Why is your offer better than others?").fill(
        f"Bookings limit test — {price}"
    )
    broker.wait_for_timeout(500)

    broker.get_by_role("button", name="Place a bid").last.click()
    broker.wait_for_timeout(5000)

    # ─── load_owner: bid'ni accept qilish ───────────────────
    load_owner.goto(f"{APP_URL}/profile/root")
    load_owner.wait_for_timeout(3000)
    load_owner.get_by_text("Received bids", exact=True).first.click()
    load_owner.wait_for_timeout(5000)

    load_owner.get_by_text(price_pattern).first.click()
    load_owner.wait_for_timeout(2500)

    bid_button = (
        load_owner.get_by_role("button")
        .filter(has_text=price_pattern)
        .filter(has_text=re.compile(r"broker", re.IGNORECASE))
        .first
    )
    bid_button.click()
    load_owner.wait_for_timeout(2000)

    load_owner.get_by_role("button", name="Accept").click()
    load_owner.wait_for_timeout(5000)


# ──────────────────── Testlar ────────────────────────────────


@pytest.mark.xfail(reason="Bookings limit enforcement ishlamayapti — backend bug: 5/5 dan oshsa ham booking o'tib ketmoqda")
@allure.feature("Plan Limits")
@allure.story("Free plan: fill bookings to limit and verify 'Limit reached' modal")
@allure.severity(allure.severity_level.CRITICAL)
def test_bookings_limit_full_flow(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Broker 5 ta booking yaratib, 6-chisida 'Limit reached' modal
    chiqishini tekshiradi.

    1. Usage'dan hozirgi bookings sonini o'qish
    2. 5 gacha to'ldirish (har biri: yuk → bid → accept)
    3. 6-chi accept'da modal chiqishi kerak
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    # ─── Hozirgi holatni o'qish ─────────────────────────────
    current = _read_bookings_count(broker)
    needed = BOOKINGS_LIMIT - current
    print(f"\n[BOOKINGS] Hozirgi: {current}/{BOOKINGS_LIMIT}, kerakli: {needed} ta booking")

    # ─── Limit'gacha to'ldirish ──────────────────────────────
    for i in range(needed):
        booking_num = current + i + 1
        price = str(10000 + booking_num)
        print(f"[BOOKINGS] Booking #{booking_num}/{BOOKINGS_LIMIT} yaratilmoqda (price: {price})...")
        _create_booking(owner, broker, price)

    # ─── Limitga yetganini tasdiqlash ────────────────────────
    final = _read_bookings_count(broker)
    assert final >= BOOKINGS_LIMIT, (
        f"Kutilgan >= {BOOKINGS_LIMIT}/{BOOKINGS_LIMIT}, haqiqiy {final}/{BOOKINGS_LIMIT}"
    )
    print(f"[BOOKINGS] Tasdiqlandi: {final}/{BOOKINGS_LIMIT}")

    # ─── 6-chi booking: modal chiqishi kerak ─────────────────
    print("[BOOKINGS] 6-chi booking yaratilmoqda (modal kutilmoqda)...")
    _create_booking(owner, broker, str(10000 + BOOKINGS_LIMIT + 1))

    # ─── Modal verifikatsiya ─────────────────────────────────
    # Modal broker yoki load_owner sahifasida chiqishi mumkin
    # (6-chi bid yuborishda broker bloklanadi, accept'da load_owner)
    modal_page = None
    for p in [broker, owner]:
        try:
            p.get_by_role("heading", name="Limit reached").wait_for(
                state="visible", timeout=5000
            )
            modal_page = p
            break
        except Exception:
            pass

    assert modal_page is not None, "Hech qaysi sahifada 'Limit reached' modal topilmadi"

    expect(modal_page.get_by_text("You have reached your limit")).to_be_visible()
    expect(modal_page.get_by_role("button", name="Upgrade plan")).to_be_visible()
    expect(modal_page.get_by_role("button", name="Maybe later")).to_be_visible()

    print(f"[BOOKINGS] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("Bookings limit modal: 'Maybe later' dismisses modal")
@allure.severity(allure.severity_level.NORMAL)
def test_bookings_modal_maybe_later(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Broker bookings limit'da bo'lganda, 'Maybe later' bosilganda
    modal yopilishini tekshiradi.

    Pre-condition: broker 5/5 bo'lishi kerak.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    current = _read_bookings_count(broker)
    if current < BOOKINGS_LIMIT:
        pytest.skip(
            f"Broker {current}/{BOOKINGS_LIMIT} holatda. Avval "
            f"test_bookings_limit_full_flow ni ishga tushiring."
        )

    _create_booking(owner, broker, "19001")

    expect(
        broker.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    broker.get_by_role("button", name="Maybe later").click()
    broker.wait_for_timeout(1000)

    expect(
        broker.get_by_role("heading", name="Limit reached")
    ).not_to_be_visible()

    print("[MODAL] ✅ 'Maybe later' bosildi — modal yopildi!")


@allure.feature("Plan Limits")
@allure.story("Bookings limit modal: 'Upgrade plan' navigates to upgrade page")
@allure.severity(allure.severity_level.NORMAL)
def test_bookings_modal_upgrade_plan(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Broker bookings limit'da bo'lganda, 'Upgrade plan' bosilganda
    upgrade sahifasiga o'tishini tekshiradi.

    Pre-condition: broker 5/5 bo'lishi kerak.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    current = _read_bookings_count(broker)
    if current < BOOKINGS_LIMIT:
        pytest.skip(
            f"Broker {current}/{BOOKINGS_LIMIT} holatda. Avval "
            f"test_bookings_limit_full_flow ni ishga tushiring."
        )

    _create_booking(owner, broker, "19002")

    expect(
        broker.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    broker.get_by_role("button", name="Upgrade plan").click()
    broker.wait_for_timeout(3000)

    expect(broker).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)

    print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
