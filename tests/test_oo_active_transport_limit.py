"""
Owner Operator — Active transport limit enforcement testlari.

Stsenariy:
1. OO 1 ta trip yaratadi (0 → 1/1)
2. 2-chi trip yaratishda "Limit reached" modal chiqadi
3. Modal behavior: "Maybe later"/"Close" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Free plan: Active transport limit = 1.
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

TRANSPORT_LIMIT = 1


# ──────────────────── Helper funksiyalar ────────────────────


def _read_active_transport(page: Page) -> int:
    """OO'ning joriy 'Active transport' qiymatini Usage sahifasidan o'qish."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    card = (
        page.locator("div")
        .filter(has_text="Active transport")
        .filter(has_text=f"/ {TRANSPORT_LIMIT}")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(rf"(\d+)\s*/\s*{TRANSPORT_LIMIT}", text)
    assert match, f"'Active transport' formatida son topilmadi:\n{text}"
    return int(match.group(1))


def _create_one_trip(page: Page, price: int) -> None:
    """OO uchun trip yaratadi."""
    TripsPage(page).create_trip(
        transport="Trailer 1",
        volume=10,
        loading_city="tashkent",
        loading_suggestion="Tashkent",
        loading_radius=12,
        unloading_city="denov",
        unloading_suggestion="Denov District",
        unloading_radius=12,
        price=price,
    )
    page.wait_for_timeout(3000)


# ──────────────────── Testlar ────────────────────────────────


@pytest.mark.xfail(reason="BUG: Active transport limit enforce qilinmayapti — limitdan oshsa ham trip yaratiladi")
@allure.feature("Plan Limits")
@allure.story("Owner Operator Free plan: active transport limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_oo_active_transport_limit_full_flow(logged_in_owner_operator: Page):
    """
    OO 1 ta trip yaratib, 2-chisida 'Limit reached' modal
    chiqishini tekshiradi.
    """
    page = logged_in_owner_operator
    page.set_default_timeout(60000)

    current = _read_active_transport(page)
    needed = max(0, TRANSPORT_LIMIT - current)
    print(f"\n[TRANSPORT] Hozirgi: {current}/{TRANSPORT_LIMIT}, kerakli: {needed}")

    for i in range(needed):
        num = current + i + 1
        price = 8000 + num
        print(f"[TRANSPORT] Trip #{num}/{TRANSPORT_LIMIT} yaratilmoqda (price: {price})...")
        _create_one_trip(page, price)

    final = _read_active_transport(page)
    assert final >= TRANSPORT_LIMIT, (
        f"Kutilgan >= {TRANSPORT_LIMIT}/{TRANSPORT_LIMIT}, haqiqiy {final}/{TRANSPORT_LIMIT}"
    )
    print(f"[TRANSPORT] Tasdiqlandi: {final}/{TRANSPORT_LIMIT}")

    print("[TRANSPORT] 2-chi trip yaratilmoqda (modal kutilmoqda)...")
    _create_one_trip(page, 8000 + TRANSPORT_LIMIT + 1)

    # Modal — "Limit reached" yoki dialog
    modal_heading = page.get_by_role("heading", name="Limit reached")
    modal_dialog = page.get_by_role("dialog", name="Limit reached")

    expect(modal_heading.or_(modal_dialog)).to_be_visible(timeout=10000)

    print("[TRANSPORT] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@pytest.mark.xfail(reason="BUG: Active transport limit enforce qilinmayapti — modal chiqmaydi")
@allure.feature("Plan Limits")
@allure.story("Owner Operator: active transport modal — dismiss")
@allure.severity(allure.severity_level.NORMAL)
def test_oo_active_transport_modal_dismiss(logged_in_owner_operator: Page):
    """'Maybe later' yoki 'Close' bosilganda modal yopilishini tekshiradi."""
    page = logged_in_owner_operator
    page.set_default_timeout(60000)

    current = _read_active_transport(page)
    if current < TRANSPORT_LIMIT:
        pytest.skip(
            f"OO {current}/{TRANSPORT_LIMIT} holatda. Avval "
            f"test_oo_active_transport_limit_full_flow ni ishga tushiring."
        )

    _create_one_trip(page, 9005)

    modal_heading = page.get_by_role("heading", name="Limit reached")
    modal_dialog = page.get_by_role("dialog", name="Limit reached")
    expect(modal_heading.or_(modal_dialog)).to_be_visible(timeout=10000)

    # "Maybe later" yoki "Close" — qaysi biri bo'lsa
    maybe_later = page.get_by_role("button", name="Maybe later")
    close_btn = page.get_by_role("button", name="Close")
    if maybe_later.is_visible(timeout=2000):
        maybe_later.click()
    else:
        close_btn.click()
    page.wait_for_timeout(1000)

    expect(modal_heading.or_(modal_dialog)).not_to_be_visible()

    print("[MODAL] ✅ Modal yopildi!")


@pytest.mark.xfail(reason="BUG: Active transport limit enforce qilinmayapti — modal chiqmaydi")
@allure.feature("Plan Limits")
@allure.story("Owner Operator: active transport modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_oo_active_transport_modal_upgrade_plan(logged_in_owner_operator: Page):
    """'Upgrade plan' bosilganda upgrade sahifasiga o'tishini tekshiradi."""
    page = logged_in_owner_operator
    page.set_default_timeout(60000)

    current = _read_active_transport(page)
    if current < TRANSPORT_LIMIT:
        pytest.skip(
            f"OO {current}/{TRANSPORT_LIMIT} holatda. Avval "
            f"test_oo_active_transport_limit_full_flow ni ishga tushiring."
        )

    _create_one_trip(page, 9006)

    modal_heading = page.get_by_role("heading", name="Limit reached")
    modal_dialog = page.get_by_role("dialog", name="Limit reached")
    expect(modal_heading.or_(modal_dialog)).to_be_visible(timeout=10000)

    upgrade_btn = page.get_by_role("button", name="Upgrade plan")
    if upgrade_btn.is_visible(timeout=3000):
        upgrade_btn.click()
        page.wait_for_timeout(3000)
        expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
        print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
    else:
        pytest.skip("Modal'da 'Upgrade plan' tugmasi topilmadi")
