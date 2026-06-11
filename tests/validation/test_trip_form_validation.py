"""
Trip form validation — Next button should not advance when required fields are missing.
"""
import allure
from playwright.sync_api import Page, expect
from pages.trips_page import TripsPage


@allure.feature("Validation")
@allure.story("Trip form: empty form blocks Next")
def test_empty_form_blocks_next(logged_in_broker: Page):
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    expect(trips.transport_combobox).to_be_visible()
    trips.accept_cookies_if_visible()

    trips.next_button.click()
    expect(trips.price_input).not_to_be_visible()


@allure.feature("Validation")
@allure.story("Trip form: missing volume blocks Next")
def test_missing_volume_blocks_next(logged_in_broker: Page):
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    expect(trips.transport_combobox).to_be_visible()
    trips.accept_cookies_if_visible()

    trips.select_transport("Trailer 1")
    trips.select_lifting_capacity()
    trips.fill_loading("tashkent", "Tashkent")
    trips.fill_loading_radius(12)
    trips.fill_unloading("denov", "Denov District")
    trips.fill_unloading_radius(12)

    trips.next_button.click()
    expect(trips.price_input).not_to_be_visible()


@allure.feature("Validation")
@allure.story("Trip form: zero volume blocks Next")
def test_zero_volume_blocks_next(logged_in_broker: Page):
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    expect(trips.transport_combobox).to_be_visible()
    trips.accept_cookies_if_visible()

    trips.select_transport("Trailer 1")
    trips.select_lifting_capacity()
    trips.fill_volume(0)
    trips.fill_loading("tashkent", "Tashkent")
    trips.fill_loading_radius(12)
    trips.fill_unloading("denov", "Denov District")
    trips.fill_unloading_radius(12)

    trips.next_button.click()
    expect(trips.price_input).not_to_be_visible()


@allure.feature("Validation")
@allure.story("Trip form: negative volume blocks Next")
def test_negative_volume_blocks_next(logged_in_broker: Page):
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    expect(trips.transport_combobox).to_be_visible()
    trips.accept_cookies_if_visible()

    trips.select_transport("Trailer 1")
    trips.select_lifting_capacity()
    trips.fill_volume(-10)
    trips.fill_loading("tashkent", "Tashkent")
    trips.fill_loading_radius(12)
    trips.fill_unloading("denov", "Denov District")
    trips.fill_unloading_radius(12)

    trips.next_button.click()
    expect(trips.price_input).not_to_be_visible()
