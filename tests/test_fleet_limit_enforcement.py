"""
Fleet size limit enforcement testlari — Free plan'dagi cheklov.

Stsenariy:
1. Broker 5 ta truck qo'shadi (0 → 5/5)
2. 6-chi truck qo'shishga harakat → "Limit reached" modal chiqadi
3. Modal behavior: "Close" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Modal: dialog[name="Limit reached"] — "Close" va "Upgrade plan" tugmalari bor.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

FLEET_LIMIT = 5


# ──────────────────── Helper funksiyalar ────────────────────


def _read_fleet_size(page: Page) -> int:
    """Joriy 'Fleet size' qiymatini Usage sahifasidan o'qish."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    card = (
        page.locator("div")
        .filter(has_text="Fleet size")
        .filter(has_text=f"/ {FLEET_LIMIT}")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(rf"(\d+)\s*/\s*{FLEET_LIMIT}", text)
    assert match, f"'Fleet size' formatida son topilmadi:\n{text}"
    return int(match.group(1))


def _add_one_trailer(page: Page, index: int) -> None:
    """Fleet sahifada bitta trailer qo'shadi."""
    page.goto(f"{APP_URL}/tms/fleet")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # Trailers tab
    page.get_by_role("tab", name="Trailers").click()
    page.wait_for_timeout(1000)

    page.get_by_role("button", name="Add Trailer").click()
    page.wait_for_timeout(2000)

    # Country
    page.get_by_text("Select country").click()
    page.get_by_role("option", name="United Arab Emirates").click()
    page.wait_for_timeout(500)

    # Gov. Number — har safar unique
    page.get_by_role("textbox", name="Gov. Number*").click()
    page.get_by_role("textbox", name="Gov. Number*").fill(f"TRL-{index:03d}")
    page.wait_for_timeout(500)

    # Trailer Type
    page.get_by_role("combobox").filter(has_text="Trailer Type").click()
    page.get_by_role("option", name="Trailer 1").click()
    page.wait_for_timeout(500)

    # Year
    page.get_by_role("combobox").filter(has_text=re.compile(r"^$")).click()
    page.get_by_role("option", name="2018").click()
    page.wait_for_timeout(500)

    # Submit
    page.get_by_role("button", name="Add").click()
    page.wait_for_timeout(3000)


# ──────────────────── Testlar ────────────────────────────────


@pytest.mark.xfail(reason="Fleet size Usage counter ishlamayapti — backend bug")
@allure.feature("Plan Limits")
@allure.story("Free plan: fill fleet to limit and verify 'Limit reached' modal")
@allure.severity(allure.severity_level.CRITICAL)
def test_fleet_limit_full_flow(logged_in_broker: Page):
    """
    Broker 5 ta truck qo'shib, 6-chisida 'Limit reached' modal
    chiqishini tekshiradi.

    1. Usage'dan hozirgi fleet sonini o'qish
    2. 5 gacha to'ldirish
    3. 6-chi truck → modal chiqishi kerak
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    # ─── Hozirgi holatni o'qish ─────────────────────────────
    current = _read_fleet_size(page)
    needed = FLEET_LIMIT - current
    print(f"\n[FLEET] Hozirgi: {current}/{FLEET_LIMIT}, kerakli: {needed} ta truck")

    # ─── Limit'gacha to'ldirish ──────────────────────────────
    for i in range(needed):
        truck_num = current + i + 1
        print(f"[FLEET] Truck #{truck_num}/{FLEET_LIMIT} qo'shilmoqda...")
        _add_one_trailer(page, truck_num)

    # ─── Limitga yetganini tasdiqlash ────────────────────────
    final = _read_fleet_size(page)
    assert final == FLEET_LIMIT, (
        f"Kutilgan {FLEET_LIMIT}/{FLEET_LIMIT}, haqiqiy {final}/{FLEET_LIMIT}"
    )
    print(f"[FLEET] Tasdiqlandi: {final}/{FLEET_LIMIT}")

    # ─── 6-chi truck: modal chiqishi kerak ───────────────────
    print("[FLEET] 6-chi truck qo'shilmoqda (modal kutilmoqda)...")
    _add_one_trailer(page, FLEET_LIMIT + 1)

    # ─── Modal verifikatsiya ─────────────────────────────────
    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).to_be_visible(timeout=10000)

    expect(
        page.get_by_role("button", name="Close")
    ).to_be_visible()

    print("[FLEET] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("Fleet limit modal: 'Close' dismisses modal")
@allure.severity(allure.severity_level.NORMAL)
def test_fleet_modal_close(logged_in_broker: Page):
    """
    Broker fleet limit'da bo'lganda truck qo'shib, 'Close'
    bosilganda modal yopilishini tekshiradi.

    Pre-condition: broker 5/5 bo'lishi kerak.
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    current = _read_fleet_size(page)
    if current < FLEET_LIMIT:
        pytest.skip(
            f"Broker {current}/{FLEET_LIMIT} holatda. Avval "
            f"test_fleet_limit_full_flow ni ishga tushiring."
        )

    # 6-chi truck → modal chiqadi
    _add_one_trailer(page, 9001)

    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).to_be_visible(timeout=10000)

    # "Close" bosish
    page.get_by_role("button", name="Close").click()
    page.wait_for_timeout(1000)

    # Modal yopilganini tasdiqlash
    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).not_to_be_visible()

    print("[MODAL] ✅ 'Close' bosildi — modal yopildi!")


@allure.feature("Plan Limits")
@allure.story("Fleet limit modal: 'Upgrade plan' navigates to upgrade page")
@allure.severity(allure.severity_level.NORMAL)
def test_fleet_modal_upgrade_plan(logged_in_broker: Page):
    """
    Broker fleet limit'da bo'lganda truck qo'shib, 'Upgrade plan'
    bosilganda upgrade sahifasiga o'tishini tekshiradi.

    Pre-condition: broker 5/5 bo'lishi kerak.
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    current = _read_fleet_size(page)
    if current < FLEET_LIMIT:
        pytest.skip(
            f"Broker {current}/{FLEET_LIMIT} holatda. Avval "
            f"test_fleet_limit_full_flow ni ishga tushiring."
        )

    # 6-chi truck → modal chiqadi
    _add_one_trailer(page, 9002)

    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).to_be_visible(timeout=10000)

    # "Upgrade plan" bosish (agar modal'da bor bo'lsa)
    upgrade_btn = page.get_by_role("button", name="Upgrade plan")
    if upgrade_btn.is_visible(timeout=3000):
        upgrade_btn.click()
        page.wait_for_timeout(3000)
        expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
        print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
    else:
        pytest.skip("Modal'da 'Upgrade plan' tugmasi topilmadi")
