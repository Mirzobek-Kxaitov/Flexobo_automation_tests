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

SEARCH_ROLES = ["broker", "carrier", "owner_operator"]


def _open_loads_board(page: Page):
    page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")
    expect(page.get_by_test_id("loads_search_from_input")).to_be_visible(timeout=15000)


@allure.feature("Loads search")
@allure.story("Search form is visible to all logged-in roles")
@pytest.mark.parametrize("role", SEARCH_ROLES)
def test_search_form_visible(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    _open_loads_board(page)

    expect(page.get_by_test_id("loads_search_from_input")).to_be_visible()
    expect(page.get_by_test_id("loads_search_to_input")).to_be_visible()
    expect(page.get_by_test_id("loads_search_button")).to_be_visible()
    expect(page.get_by_test_id("loads_filter_button")).to_be_visible()


@allure.feature("Loads search")
@allure.story("Search by 'From' city filters results")
def test_search_by_from_city_returns_matching_loads(logged_in_broker: Page):
    page = logged_in_broker
    _open_loads_board(page)

    page.get_by_test_id("loads_search_from_input").fill("Tashkent")
    page.get_by_text("Tashkent", exact=False).first.click()

    page.get_by_test_id("loads_search_button").click()
    expect(page.get_by_text("Tashkent").first).to_be_visible(timeout=10000)


@allure.feature("Loads search")
@allure.story("Filter button opens filter panel")
def test_filter_button_opens_panel(logged_in_broker: Page):
    page = logged_in_broker
    _open_loads_board(page)

    page.get_by_test_id("loads_filter_button").click()
    expect(page.get_by_test_id("loads_filter_panel")).to_be_visible()
    expect(page.get_by_test_id("loads_filter_apply_button")).to_be_visible()
    expect(page.get_by_test_id("loads_filter_reset_button")).to_be_visible()
