import allure
import pytest
from playwright.sync_api import Page
from pages.profile_page import ProfilePage
from pages.loads_page import LoadsPage


# Yuk yaratish/edit/delete uchun ruxsati bor role'lar
LOAD_CAPABLE_ROLES = ["broker", "load_owner"]


@allure.feature("Loads")
@allure.story("Create load")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", LOAD_CAPABLE_ROLES)
def test_create_load(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    LoadsPage(page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        body_type="Mega truck",
        price="1000",
    ).expect_load_created()


@allure.feature("Loads")
@allure.story("Loads page accessible")
@pytest.mark.parametrize("role", LOAD_CAPABLE_ROLES)
def test_loads_page_is_accessible(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_my_loads()
    LoadsPage(page).expect_on_loads_page()


@allure.feature("Loads")
@allure.story("Filter: In Contract")
@pytest.mark.parametrize("role", LOAD_CAPABLE_ROLES)
def test_in_contract_filter_on_loads_page(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_my_loads()
    LoadsPage(page).toggle_in_contract_filter().expect_in_contract_checked()


@allure.feature("Loads")
@allure.story("Filter: In Transit")
@pytest.mark.parametrize("role", LOAD_CAPABLE_ROLES)
def test_in_transit_filter_on_loads_page(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_my_loads()
    LoadsPage(page).toggle_in_transit_filter().expect_in_transit_checked()


@allure.feature("Loads")
@allure.story("Filter: Delivered")
@pytest.mark.parametrize("role", LOAD_CAPABLE_ROLES)
def test_delivered_filter_on_loads_page(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_my_loads()
    LoadsPage(page).toggle_delivered_filter().expect_delivered_checked()


@allure.feature("Loads")
@allure.story("Edit load")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", LOAD_CAPABLE_ROLES)
def test_edit_load(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    LoadsPage(page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        body_type="Mega truck",
        price="1000",
    ).expect_load_created()

    ProfilePage(page).go_to_my_loads()
    LoadsPage(page).edit_load(
        from_city="Samarkand",
        from_suggestion="Samarkand, Samarkand Province, 140000, Uzbekistan",
        to_city="Tashkent",
        to_suggestion="Tashkent, 100000, Uzbekistan",
        weight="30",
        price="2000",
    ).expect_on_loads_page()


@allure.feature("Loads")
@allure.story("Delete load")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", LOAD_CAPABLE_ROLES)
def test_delete_load(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")

    LoadsPage(page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        body_type="Mega truck",
        price="1000",
    ).expect_load_created()

    ProfilePage(page).go_to_my_loads()
    LoadsPage(page).delete_first_load().expect_on_loads_page()
