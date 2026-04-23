import allure
from playwright.sync_api import Page
from pages.trips_page import TripsPage


@allure.feature("Trips")
@allure.story("Add trip")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_trip(logged_in: Page):
    TripsPage(logged_in).create_trip(
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
def test_edit_trip(logged_in: Page):
    # 1. Avval trip yaratamiz
    trips = TripsPage(logged_in)
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

    # 2. My Trips ga o'tamiz va birinchi trip narxini o'zgartiramiz
    logged_in.goto(f"https://app.flexobo-mock.site/profile-trips")
    trips.edit_trip(price=2500).expect_on_trips_page()


@allure.feature("Trips")
@allure.story("Delete trip")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_trip(logged_in: Page):
    # 1. Avval trip yaratamiz
    trips = TripsPage(logged_in)
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

    # 2. My Trips ga o'tamiz va birinchi tripni o'chiramiz
    logged_in.goto(f"https://app.flexobo-mock.site/profile-trips")
    trips.delete_first_trip().expect_on_trips_page()
