from playwright.sync_api import Page
from pages.profile_page import ProfilePage

def test_profile_page(logged_in: Page):
    ProfilePage(logged_in).go_to_profile().expect_on_profile_page()

def test_my_loads_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_loads().expect_my_loads_page()

def test_my_trucks_page(logged_in: Page):
    ProfilePage(logged_in).go_to_fleet().expect_fleet_page()

def test_my_trips_page(logged_in: Page):
    ProfilePage(logged_in).go_to_my_trips().expect_my_trips_page()

def test_user_can_logout(logged_in: Page):
    ProfilePage(logged_in).logout().expect_logged_out()
