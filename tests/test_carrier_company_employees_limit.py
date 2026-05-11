"""
Carrier — Company employees limit enforcement testlari.

Stsenariy:
1. Carrier 2 ta employee qo'shadi (0 → 2/2)
2. 3-chi employee qo'shishda "Limit reached" modal chiqadi
3. Modal behavior: "Maybe later" (yopiladi), "Upgrade plan" (sahifa o'tadi)

Free plan: Company employees limit = 2.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

EMPLOYEES_LIMIT = 2


# ──────────────────── Helper funksiyalar ────────────────────


def _read_company_employees_count(page: Page) -> int:
    """Carrier'ning joriy 'Company employees' qiymatini Usage sahifasidan o'qish."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    card = (
        page.locator("div")
        .filter(has_text="Company employees")
        .filter(has_text=f"/ {EMPLOYEES_LIMIT}")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(rf"(\d+)\s*/\s*{EMPLOYEES_LIMIT}", text)
    assert match, f"'Company employees' formatida son topilmadi:\n{text}"
    return int(match.group(1))


def _add_one_employee(page: Page, index: int) -> None:
    """Profile → Users tab → employee qo'shadi."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    page.get_by_role("tab", name="Users").click()
    page.wait_for_timeout(1500)

    page.get_by_role("button", name="Invite User").click()
    page.wait_for_timeout(1500)

    # Phone or Email
    page.get_by_role("textbox", name="Phone or Email").fill(
        f"carrier_emp_{index}@test.com"
    )
    page.wait_for_timeout(500)

    # Role tanlash
    page.get_by_role("combobox", name="Role").click()
    page.get_by_role("option").first.click()
    page.wait_for_timeout(500)

    # Submit
    page.get_by_role("button", name="Send Invitation").click()
    page.wait_for_timeout(3000)


# ──────────────────── Testlar ────────────────────────────────


@pytest.mark.xfail(reason="BUG: Company employees Usage counter ishlamayapti — invite yuboriladi lekin counter 0 qoladi")
@allure.feature("Plan Limits")
@allure.story("Carrier Free plan: company employees limit enforcement")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_company_employees_limit_full_flow(logged_in_carrier: Page):
    """
    Carrier 2 ta employee qo'shib, 3-chisida 'Limit reached' modal
    chiqishini tekshiradi.
    """
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_company_employees_count(page)
    needed = max(0, EMPLOYEES_LIMIT - current)
    print(f"\n[EMPLOYEES] Hozirgi: {current}/{EMPLOYEES_LIMIT}, kerakli: {needed}")

    for i in range(needed):
        num = current + i + 1
        print(f"[EMPLOYEES] Employee #{num}/{EMPLOYEES_LIMIT} qo'shilmoqda...")
        _add_one_employee(page, num)

    final = _read_company_employees_count(page)
    assert final >= EMPLOYEES_LIMIT, (
        f"Kutilgan >= {EMPLOYEES_LIMIT}/{EMPLOYEES_LIMIT}, haqiqiy {final}/{EMPLOYEES_LIMIT}"
    )
    print(f"[EMPLOYEES] Tasdiqlandi: {final}/{EMPLOYEES_LIMIT}")

    print("[EMPLOYEES] 3-chi employee qo'shilmoqda (modal kutilmoqda)...")
    _add_one_employee(page, EMPLOYEES_LIMIT + 1)

    expect(
        page.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    expect(page.get_by_text("You have reached your limit")).to_be_visible()
    expect(page.get_by_role("button", name="Upgrade plan")).to_be_visible()
    expect(page.get_by_role("button", name="Maybe later")).to_be_visible()

    print("[EMPLOYEES] ✅ 'Limit reached' modal muvaffaqiyatli ko'rindi!")


@allure.feature("Plan Limits")
@allure.story("Carrier: company employees limit modal — 'Maybe later' dismisses")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_employees_modal_maybe_later(logged_in_carrier: Page):
    """'Maybe later' bosilganda modal yopilishini tekshiradi."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_company_employees_count(page)
    if current < EMPLOYEES_LIMIT:
        pytest.skip(
            f"Carrier {current}/{EMPLOYEES_LIMIT} holatda. Avval "
            f"test_carrier_company_employees_limit_full_flow ni ishga tushiring."
        )

    _add_one_employee(page, 9001)

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
@allure.story("Carrier: company employees limit modal — 'Upgrade plan' navigates")
@allure.severity(allure.severity_level.NORMAL)
def test_carrier_company_employees_modal_upgrade_plan(logged_in_carrier: Page):
    """'Upgrade plan' bosilganda upgrade sahifasiga o'tishini tekshiradi."""
    page = logged_in_carrier
    page.set_default_timeout(60000)

    current = _read_company_employees_count(page)
    if current < EMPLOYEES_LIMIT:
        pytest.skip(
            f"Carrier {current}/{EMPLOYEES_LIMIT} holatda. Avval "
            f"test_carrier_company_employees_limit_full_flow ni ishga tushiring."
        )

    _add_one_employee(page, 9002)

    expect(
        page.get_by_role("heading", name="Limit reached")
    ).to_be_visible(timeout=10000)

    page.get_by_role("button", name="Upgrade plan").click()
    page.wait_for_timeout(3000)

    expect(page).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)

    print("[MODAL] ✅ 'Upgrade plan' bosildi — upgrade sahifaga o'tildi!")
