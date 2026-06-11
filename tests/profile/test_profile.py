import allure
import pytest
from playwright.sync_api import Page
from pages.profile_page import ProfilePage


# Profile sahifasi va logout — barcha role'lar uchun
ALL_ROLES = ["broker", "load_owner", "carrier", "owner_operator"]

# My Loads — faqat load egalari
LOAD_ROLES = ["broker", "load_owner"]

# Fleet va My Trips — transport bilan ishlovchi role'lar (LoadOwner emas)
TRANSPORT_ROLES = ["broker", "carrier", "owner_operator"]


@allure.feature("Profile")
@allure.story("Open profile page")
@pytest.mark.parametrize("role", ALL_ROLES)
def test_open_profile_page(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_profile().expect_on_profile_page()


@allure.feature("Profile")
@allure.story("My Loads page")
@pytest.mark.parametrize("role", LOAD_ROLES)
def test_my_loads_page(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_my_loads().expect_on_my_loads_page()


@allure.feature("Profile")
@allure.story("Fleet page")
@pytest.mark.parametrize("role", TRANSPORT_ROLES)
def test_my_trucks_page(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_fleet().expect_on_fleet_page()


@allure.feature("Profile")
@allure.story("My trips page")
@pytest.mark.parametrize("role", TRANSPORT_ROLES)
def test_my_trips_page(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).go_to_my_trips().expect_on_my_trips_page()


@allure.feature("Profile")
@allure.story("Logout")
@pytest.mark.parametrize("role", ALL_ROLES)
def test_user_can_logout(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    ProfilePage(page).logout().expect_logged_out()
