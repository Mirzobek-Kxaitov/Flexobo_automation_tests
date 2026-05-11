"""
Carrier — Company roles limit enforcement testlari.

Stsenariy:
1. Carrier 1 ta company role yaratadi (0 → 1/1)
2. 2-chi role yaratishda "Limit reached" modal chiqadi
3. Modal behavior: "Maybe later" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Free plan: Company roles limit = 1.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

ROLES_LIMIT = 1


# ──────────────────── Helper funksiyalar ────────────────────


def _read_company_roles_count(page: Page) -> int:
    """Carrier'ning joriy 'Company roles' qiymatini Usage sahifasidan o'qish."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    card = (
        page.locator("div")
        .filter(has_text="Company roles")
        .filter(has_text=f"/ {ROLES_LIMIT}")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(rf"(\d+)\s*/\s*{ROLES_LIMIT}", text)
    assert match, f"'Company roles' formatida son topilmadi:\n{text}"
    return int(match.group(1))


def _create_one_role(page: Page, name: str) -> None:
    """Profile → Roles tab → role yaratadi."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    page.get_by_role("tab", name="Roles").click()
    page.wait_for_timeout(1500)

    page.get_by_role("button", name="Create role").click()
    page.wait_for_timeout(1500)

    page.get_by_role("textbox", name="Role name").click()
    page.get_by_role("textbox", name="Role name").fill(name)
    page.wait_for_timeout(500)

    page.get_by_role("button", name="Create role").click()
    page.wait_for_timeout(3000)


# ──────────────────── Testlar ────────────────────────────────


@pytest.mark.xfail(reason="BUG: Company roles Usage counter ishlamayapti — role yaratiladi lekin counter 0 qoladi")
@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: company roles limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_company_roles_limit_full_flow(logged_in_carrier: Page):
    """
    Carrier 1 ta role yaratib, 2-chisida 'Limit reached' modal
    chiqishini tekshiradi.
    """
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_company_roles_count(page)
    needed = max(0, ROLES_LIMIT - current)
    print(f"\n[ROLES] Hozirgi: {current}/{ROLES_LIMIT}, kerakli: {needed} ta role")

    for i in range(needed):
        role_num = current + i + 1
        print(f"[ROLES] Role #{role_num}/{ROLES_LIMIT} yaratilmoqda...")
        _create_one_role(page, f"Carrier Role {role_num}")

    final = _read_company_roles_count(page)
    assert final >= ROLES_LIMIT, (
        f"Kutilgan >= {ROLES_LIMIT}/{ROLES_LIMIT}, haqiqiy {final}/{ROLES_LIMIT}"
    )
    print(f"[ROLES] Tasdiqlandi: {final}/{ROLES_LIMIT}")

    print("[ROLES] 2-chi role yaratilmoqda (modal kutilmoqda)...")
    _create_one_role(page, "Carrier Over Limit Role")

    expect(
        page.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    expect(page.get_by_text("You have reached your limit")).to_be_visible()
    expect(page.get_by_role("button", name="Upgrade plan")).to_be_visible()
    expect(page.get_by_role("button", name="Maybe later")).to_be_visible()

    print("[ROLES] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("Carrier: company roles limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_roles_modal_maybe_later(logged_in_carrier: Page):
    """'Maybe later' bosilganda modal yopilishini tekshiradi."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_company_roles_count(page)
    if current < ROLES_LIMIT:
        pytest.skip(
            f"Carrier {current}/{ROLES_LIMIT} holatda. Avval "
            f"test_carrier_company_roles_limit_full_flow ni ishga tushiring."
        )

    _create_one_role(page, "Maybe Later Role")

    expect(
        page.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    page.get_by_role("button", name="Maybe later").click()
    page.wait_for_timeout(1000)

    expect(
        page.get_by_role("heading", name="Limit reached")
    ).not_to_be_visible()

    print("[MODAL] ✅ 'Maybe later' bosildi — modal yopildi!")


@allure.feature("Plan Limits")
@allure.story("Carrier: company roles limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_roles_modal_upgrade_plan(logged_in_carrier: Page):
    """'Upgrade plan' bosilganda upgrade sahifasiga o'tishini tekshiradi."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_company_roles_count(page)
    if current < ROLES_LIMIT:
        pytest.skip(
            f"Carrier {current}/{ROLES_LIMIT} holatda. Avval "
            f"test_carrier_company_roles_limit_full_flow ni ishga tushiring."
        )

    _create_one_role(page, "Upgrade Plan Role")

    expect(
        page.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    page.get_by_role("button", name="Upgrade plan").click()
    page.wait_for_timeout(3000)

    expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)

    print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
