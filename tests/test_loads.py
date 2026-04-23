import allure
from playwright.sync_api import Page
from pages.profile_page import ProfilePage
from pages.loads_page import LoadsPage


@allure.feature("Loads")
@allure.story("Create load")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_load(logged_in: Page):
    LoadsPage(logged_in).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        day="15",
        body_type="Mega truck",
        price="1000",
    ).expect_load_created()


@allure.feature("Loads")
@allure.story("Loads page accessible")
def test_loads_page_is_accessible(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).expect_on_loads_page()


@allure.feature("Loads")
@allure.story("Filter: In Contract")
def test_in_contract_filter_on_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).toggle_in_contract_filter().expect_in_contract_checked()


@allure.feature("Loads")
@allure.story("Filter: In Transit")
def test_in_transit_filter_on_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).toggle_in_transit_filter().expect_in_transit_checked()


@allure.feature("Loads")
@allure.story("Filter: Delivered")
def test_delivered_filter_on_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).toggle_delivered_filter().expect_delivered_checked()

@allure.feature("Loads")
@allure.story("Edit load")
@allure.severity(allure.severity_level.CRITICAL)
def test_edit_load(logged_in: Page):
    LoadsPage(logged_in).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        day="15",
        body_type="Mega truck",
        price="1000",
    ).expect_load_created()

    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).edit_load(
        from_city="Samarkand",
        from_suggestion="Samarkand, Samarkand Province, 140000, Uzbekistan",
        to_city="Tashkent",
        to_suggestion="Tashkent, 100000, Uzbekistan",
        weight="30",
        price="2000",
    ).expect_on_loads_page()

    