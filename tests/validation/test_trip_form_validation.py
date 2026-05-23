"""
Trip yaratish formasini noto'g'ri ma'lumot bilan tekshirish (negative testing).

Strategiya: form yetarli to'ldirilmagan bo'lsa, "Next" tugma 2-bosqichga
(Payment step) o'tkazmasligi kerak. price_input ko'rinishi orqali tekshiramiz —
agar 1-step blok qilsa, 2-step input'lar ko'rinmaydi.
"""
import allure
from playwright.sync_api import Page, expect
from pages.trips_page import TripsPage


@allure.feature("Validation")
@allure.story("Trip form: empty form blocks Next")
def test_empty_form_blocks_next(logged_in_broker: Page):
    """Bo'sh form: Next bosilsa Payment step ochilmasligi kerak."""
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    logged_in_broker.wait_for_timeout(2000)
    trips.accept_cookies_if_visible()

    trips.next_button.click(force=True, timeout=5000)
    expect(trips.price_input).not_to_be_visible(timeout=3000)


@allure.feature("Validation")
@allure.story("Trip form: missing volume blocks Next")
def test_missing_volume_blocks_next(logged_in_broker: Page):
    """Transport, loading, unloading to'ldirilgan, lekin volume bo'sh → blocked."""
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    logged_in_broker.wait_for_timeout(2000)
    trips.accept_cookies_if_visible()

    trips.select_transport("Trailer 1")
    trips.select_lifting_capacity()
    # volume to'ldirilmadi
    trips.fill_loading("tashkent", "Tashkent")
    trips.fill_loading_radius(12)
    trips.fill_unloading("denov", "Denov District")
    trips.fill_unloading_radius(12)

    trips.next_button.click(force=True, timeout=5000)
    expect(trips.price_input).not_to_be_visible(timeout=3000)


@allure.feature("Validation")
@allure.story("Trip form: zero volume blocks Next")
def test_zero_volume_blocks_next(logged_in_broker: Page):
    """Volume=0 — qabul qilinmasligi kerak."""
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    logged_in_broker.wait_for_timeout(2000)
    trips.accept_cookies_if_visible()

    trips.select_transport("Trailer 1")
    trips.select_lifting_capacity()
    trips.fill_volume(0)
    trips.fill_loading("tashkent", "Tashkent")
    trips.fill_loading_radius(12)
    trips.fill_unloading("denov", "Denov District")
    trips.fill_unloading_radius(12)

    trips.next_button.click(force=True, timeout=5000)
    expect(trips.price_input).not_to_be_visible(timeout=3000)


@allure.feature("Validation")
@allure.story("Trip form: negative volume blocks Next")
def test_negative_volume_blocks_next(logged_in_broker: Page):
    """Volume=-10 — manfiy qiymat qabul qilinmasligi kerak."""
    trips = TripsPage(logged_in_broker)
    trips.open_create_trip_form()
    logged_in_broker.wait_for_timeout(2000)
    trips.accept_cookies_if_visible()

    logged_in_broker.wait_for_timeout(1000)
    trips.select_transport("Trailer 1")
    trips.select_lifting_capacity()
    trips.fill_volume(-10)
    trips.fill_loading("tashkent", "Tashkent")
    trips.fill_loading_radius(12)
    trips.fill_unloading("denov", "Denov District")
    trips.fill_unloading_radius(12)

    trips.next_button.click(force=True, timeout=5000)
    expect(trips.price_input).not_to_be_visible(timeout=3000)
