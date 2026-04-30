import os
import allure
import pytest
from playwright.sync_api import Page
from dotenv import load_dotenv
from pages.trips_page import TripsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")


# Trip yarata oladigan role'lar
TRIP_CAPABLE_ROLES = ["broker", "carrier", "owner_operator"]


@allure.feature("Trips")
@allure.story("Add trip")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", TRIP_CAPABLE_ROLES)
def test_add_trip(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    TripsPage(page).create_trip(
        transport="Trailer 1",
        volume=10,
        loading_city="tashkent",
        loading_suggestion="Tashkent",
        loading_radius=12,
        unloading_city="denov",
        unloading_suggestion="Denov District",
        unloading_radius=12,
        price=1200,
    ).expect_trip_in_list(
        price="USD 1,200",
        city="Tashkent",
        transport="Trailer 1",
    )


@allure.feature("Trips")
@allure.story("Edit trip")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", TRIP_CAPABLE_ROLES)
def test_edit_trip(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    trips = TripsPage(page)
    trips.create_trip(
        transport="Trailer 1",
        volume=10,
        loading_city="tashkent",
        loading_suggestion="Tashkent",
        loading_radius=12,
        unloading_city="denov",
        unloading_suggestion="Denov District",
        unloading_radius=12,
        price=1200,
    )

    page.goto(f"{APP_URL}/profile-trips")
    trips.edit_trip(price=2500).expect_on_trips_page()


@allure.feature("Trips")
@allure.story("Delete trip")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", TRIP_CAPABLE_ROLES)
def test_delete_trip(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    trips = TripsPage(page)
    trips.create_trip(
        transport="Trailer 1",
        volume=10,
        loading_city="tashkent",
        loading_suggestion="Tashkent",
        loading_radius=12,
        unloading_city="denov",
        unloading_suggestion="Denov District",
        unloading_radius=12,
        price=1200,
    )

    page.goto(f"{APP_URL}/profile-trips")
    trips.delete_first_trip().expect_on_trips_page()
