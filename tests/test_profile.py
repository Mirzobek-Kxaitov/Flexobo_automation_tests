import allure
from playwright.sync_api import Page
from pages.profile_page import ProfilePage


@allure.feature("Profile")
@allure.story("Open profile page")
def test_open_profile_page(logged_in: Page):
    ProfilePage(logged_in).go_to_profile().expect_on_profile_page()


@allure.feature("Profile")
@allure.story("My Loads page")
def test_my_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads().expect_on_my_loads_page()


@allure.feature("Profile")
@allure.story("Fleet page")
def test_my_trucks_page(logged_in: Page):
    ProfilePage(logged_in).go_to_fleet().expect_on_fleet_page()


@allure.feature("Profile")
@allure.story("My trips page")
def test_my_trips_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_trips().expect_on_my_trips_page()


@allure.feature("Profile")
@allure.story("Logout")
def test_user_can_logout(logged_in: Page):
    ProfilePage(logged_in).logout().expect_logged_out()
