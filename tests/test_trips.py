from playwright.sync_api import Page
from pages.trips_page import TripsPage

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
