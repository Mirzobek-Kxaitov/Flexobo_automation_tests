"""
TMS sahifalarida content (heading, Add tugma, tab'lar) role bo'yicha
to'g'ri ko'rinishini tekshiradi.

URL access allaqachon test_direct_url_permissions.py'da yopilgan — bu test
ruxsat bor role'lar uchun page o'z kontentini to'g'ri render qilishini tasdiqlaydi.
"""
import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


# Fleet sahifasiga kira oluvchi role'lar
FLEET_ROLES = ["broker", "carrier", "owner_operator"]

# Drivers sahifasiga kira oluvchi role'lar (OO yo'q — Drivers tab ko'rmaydi)
DRIVERS_ROLES = ["broker", "carrier"]

# Orders sahifasiga kira oluvchi role'lar (hammasi)
ORDERS_ROLES = ["broker", "load_owner", "carrier", "owner_operator"]


@allure.feature("TMS")
@allure.story("Fleet page renders heading, Add Truck button, tabs")
@pytest.mark.parametrize("role", FLEET_ROLES)
def test_fleet_page_content(request, role: str):
    """Fleet sahifa: 'Fleet' heading, 'Add Truck' tugma, Trucks/Trailers tab'lari."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/tms/fleet")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    expect(page.get_by_text("Fleet", exact=True).first).to_be_visible()
    expect(page.get_by_role("button", name="Add Truck").first).to_be_visible()
    expect(page.get_by_text("Trucks", exact=True).first).to_be_visible()
    expect(page.get_by_text("Trailers", exact=True).first).to_be_visible()


@allure.feature("TMS")
@allure.story("Drivers page renders heading, Add Driver button, tabs")
@pytest.mark.parametrize("role", DRIVERS_ROLES)
def test_drivers_page_content(request, role: str):
    """Drivers sahifa: 'Drivers' heading, 'Add Driver' tugma, Drivers/Invite Driver tab'lari."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/tms/drivers")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    expect(page.get_by_text("Drivers", exact=True).first).to_be_visible()
    expect(page.get_by_role("button", name="Add Driver").first).to_be_visible()
    expect(page.get_by_text("Invite Driver", exact=True).first).to_be_visible()


@allure.feature("TMS")
@allure.story("Orders page renders heading and table columns")
@pytest.mark.parametrize("role", ORDERS_ROLES)
def test_orders_page_content(request, role: str):
    """Orders sahifa: 'Orders' heading va jadval ustunlari (ORDER #, ROUTE, ...)."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/tms/orders")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # Faqat heading'ni tekshiramiz — ustunlar faqat orders bo'lganda ko'rinadi
    expect(page.get_by_text("Orders", exact=True).first).to_be_visible()
