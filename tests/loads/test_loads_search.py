"""
Loads search/board funksionalligini tekshirish.
/loads sahifasi — yuk qidiruv board, hamma role'lar uchun ochiq.
"""
import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.loads_board_page import LoadsBoardPage

load_dotenv()
APP_URL = os.getenv("APP_URL")

SEARCH_ROLES = ["broker", "carrier", "owner_operator"]


@allure.feature("Loads search")
@allure.story("Search form is visible to all logged-in roles")
@pytest.mark.parametrize("role", SEARCH_ROLES)
def test_search_form_visible(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    LoadsBoardPage(page).open(APP_URL).expect_search_form_visible()


@allure.feature("Loads search")
@allure.story("Search by 'From' city filters results")
def test_search_by_from_city_returns_matching_loads(logged_in_broker: Page):
    board = LoadsBoardPage(logged_in_broker).open(APP_URL)
    board.search_from_city("Tashkent")
    board.click_search()
    expect(logged_in_broker.get_by_text("Tashkent").first).to_be_visible(timeout=10000)


@allure.feature("Loads search")
@allure.story("Filter button opens filter panel")
def test_filter_button_opens_panel(logged_in_broker: Page):
    board = LoadsBoardPage(logged_in_broker).open(APP_URL)
    board.open_filter_panel()
    board.expect_filter_panel_visible()
