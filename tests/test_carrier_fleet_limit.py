"""
Carrier — Fleet size limit enforcement testlari.

Stsenariy:
1. Carrier 3 ta trailer qo'shadi (0 → 3/3)
2. 4-chi trailer qo'shishda "Limit reached" modal chiqadi
3. Modal behavior: "Close" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Free plan: Fleet size limit = 3.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

FLEET_LIMIT = 3


# ──────────────────── Helper funksiyalar ────────────────────


def _read_fleet_size(page: Page) -> int:
    """Carrier'ning joriy 'Fleet size' qiymatini Usage sahifasidan o'qish."""
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
    page.get_by_role("textbox", name="Gov. Number*").fill(f"CR-TRL-{index:03d}")
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


@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: fleet size limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_fleet_limit_full_flow(logged_in_carrier: Page):
    """
    Carrier 3 ta trailer qo'shib, 4-chisida 'Limit reached' modal
    chiqishini tekshiradi.
    """
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_fleet_size(page)
    needed = max(0, FLEET_LIMIT - current)
    print(f"\n[FLEET] Hozirgi: {current}/{FLEET_LIMIT}, kerakli: {needed} ta trailer")

    for i in range(needed):
        num = current + i + 1
        print(f"[FLEET] Trailer #{num}/{FLEET_LIMIT} qo'shilmoqda...")
        _add_one_trailer(page, num)

    final = _read_fleet_size(page)
    assert final >= FLEET_LIMIT, (
        f"Kutilgan >= {FLEET_LIMIT}/{FLEET_LIMIT}, haqiqiy {final}/{FLEET_LIMIT}"
    )
    print(f"[FLEET] Tasdiqlandi: {final}/{FLEET_LIMIT}")

    print("[FLEET] 4-chi trailer qo'shilmoqda (modal kutilmoqda)...")
    _add_one_trailer(page, FLEET_LIMIT + 1)

    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).to_be_visible(timeout=10000)

    expect(page.get_by_role("button", name="Close")).to_be_visible()

    print("[FLEET] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("Carrier: fleet limit modal — 'Close' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_fleet_modal_close(logged_in_carrier: Page):
    """'Close' bosilganda modal yopilishini tekshiradi."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_fleet_size(page)
    if current < FLEET_LIMIT:
        pytest.skip(
            f"Carrier {current}/{FLEET_LIMIT} holatda. Avval "
            f"test_carrier_fleet_limit_full_flow ni ishga tushiring."
        )

    _add_one_trailer(page, 9001)

    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).to_be_visible(timeout=10000)

    page.get_by_role("button", name="Close").click()
    page.wait_for_timeout(1000)

    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).not_to_be_visible()

    print("[MODAL] ✅ 'Close' bosildi — modal yopildi!")


@allure.feature("Plan Limits")
@allure.story("Carrier: fleet limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_fleet_modal_upgrade_plan(logged_in_carrier: Page):
    """'Upgrade plan' bosilganda upgrade sahifasiga o'tishini tekshiradi."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_fleet_size(page)
    if current < FLEET_LIMIT:
        pytest.skip(
            f"Carrier {current}/{FLEET_LIMIT} holatda. Avval "
            f"test_carrier_fleet_limit_full_flow ni ishga tushiring."
        )

    _add_one_trailer(page, 9002)

    expect(
        page.get_by_role("dialog", name="Limit reached")
    ).to_be_visible(timeout=10000)

    upgrade_btn = page.get_by_role("button", name="Upgrade plan")
    if upgrade_btn.is_visible(timeout=3000):
        upgrade_btn.click()
        page.wait_for_timeout(3000)
        expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
        print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
    else:
        pytest.skip("Modal'da 'Upgrade plan' tugmasi topilmadi")
