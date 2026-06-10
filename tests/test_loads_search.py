"""
Loads search/board funksionalligini tekshirish.
/loads sahifasi — yuk qidiruv board, hamma role'lar uchun ochiq.

Form: From + To placeholder'lar, When + Search tugmalari.
"""
import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

# LoadOwner bu sahifaga turli holatda redirect bo'ladi, search form ko'rinmaydi.
# Search board asosan transport-tomon role'lar uchun (yuk topish uchun).
SEARCH_ROLES = ["broker", "carrier", "owner_operator"]


@allure.feature("Loads search")
@allure.story("Search form is visible to all logged-in roles")
@pytest.mark.parametrize("role", SEARCH_ROLES)
def test_search_form_visible(request, role: str):
    """Hamma role'lar /loads board'da search form'ni ko'radi."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    expect(page.get_by_test_id("loads_search_from_input")).to_be_visible()
    expect(page.get_by_test_id("loads_search_to_input")).to_be_visible()
    expect(page.get_by_test_id("loads_search_button")).to_be_visible()
    expect(page.get_by_test_id("loads_filter_button")).to_be_visible()


@allure.feature("Loads search")
@allure.story("Search by 'From' city filters results")
def test_search_by_from_city_returns_matching_loads(logged_in_broker: Page):
    """From=Tashkent qidirsak, natija'da Tashkent matni bo'lishi kerak."""
    page = logged_in_broker
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    page.get_by_test_id("loads_search_from_input").fill("Tashkent")
    page.wait_for_timeout(2000)
    # Suggestion ro'yxatidan birinchisini tanlash
    page.get_by_text("Tashkent", exact=False).first.click()
    page.wait_for_timeout(1000)

    page.get_by_test_id("loads_search_button").click()
    page.wait_for_timeout(3000)

    # Natijada hech bo'lmasa bitta "Tashkent" matni bo'lishi kerak
    expect(page.get_by_text("Tashkent").first).to_be_visible(timeout=10000)


@allure.feature("Loads search")
@allure.story("Filter button opens filter panel")
def test_filter_button_opens_panel(logged_in_broker: Page):
    """'Filter' tugmasini bosganda filter paneli ochiladi."""
    page = logged_in_broker
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    page.get_by_test_id("loads_filter_button").click()
    expect(page.get_by_test_id("loads_filter_panel")).to_be_visible()
    expect(page.get_by_test_id("loads_filter_apply_button")).to_be_visible()
    expect(page.get_by_test_id("loads_filter_reset_button")).to_be_visible()
