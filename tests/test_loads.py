from playwright.sync_api import Page
from pages.profile_page import ProfilePage
from pages.loads_page import LoadsPage

def test_loads_page_is_accessible(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).expect_on_loads_page()

def test_in_contract_filter_on_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).toggle_in_contract_filter().expect_in_contract_checked()

def test_in_transit_filter_on_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).toggle_in_transit_filter().expect_in_transit_checked()

def test_delivered_filter_on_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads()
    LoadsPage(logged_in).toggle_delivered_filter().expect_delivered_checked()

def test_create_load(logged_in: Page):
    LoadsPage(logged_in).create_load(
        from_city="tashkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        day="10",
        body_type="Mega truck",
        price="1000"
    ).expect_load_created()
