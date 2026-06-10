import os
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")


class TripsPage:

    CREATE_URL = f"{APP_URL}/trips/create"
    LIST_URL = f"{APP_URL}/trips"

    def __init__(self, page: Page):
        self.page = page

        self.cookie_accept_button = page.get_by_test_id("global_cookie_accept_button")

        self.transport_combobox = (
            page.get_by_test_id("trips_transport_select")
            .or_(page.get_by_role("combobox").first)
            .first
        )
        self.unit_combobox = (
            page.get_by_test_id("trips_unit_select")
            .or_(page.get_by_role("combobox").filter(has_text="Choose"))
            .first
        )
        self.volume_input = page.get_by_test_id("trips_volume_input")
        self.loading_input = page.get_by_test_id("trips_loading_input")
        self.loading_radius_input = page.get_by_test_id("trips_loading_radius_input")
        self.unloading_input = page.get_by_test_id("trips_unloading_input")
        self.unloading_radius_input = page.get_by_test_id("trips_unloading_radius_input")

        self.price_input = (
            page.get_by_test_id("trips_price_input")
            .or_(page.get_by_role("textbox", name="Price*"))
            .first
        )

        self.transport_tab = page.get_by_test_id("loads_tab_transport_button").or_(
            page.get_by_role("tab", name="Transport")
        ).first

        self.next_button = page.get_by_test_id("trips_next_button")

        self.confirm_delete_button = (
            page.get_by_test_id("trips_delete_confirm_button")
            .or_(page.get_by_role("button", name="Delete", exact=True))
            .first
        )

    def open_create_trip_form(self) -> "TripsPage":
        self.page.goto(self.CREATE_URL, wait_until="domcontentloaded")
        return self

    def accept_cookies_if_visible(self) -> "TripsPage":
        if self.cookie_accept_button.is_visible():
            self.cookie_accept_button.click()
        return self

    def select_transport(self, name: str) -> "TripsPage":
        self.transport_combobox.click()
        self.page.get_by_role("option", name=name).click()
        return self

    def select_lifting_capacity(self, capacity: str = "tons") -> "TripsPage":
        self.unit_combobox.click()
        self.page.get_by_role("option", name=capacity).click()
        return self

    def fill_volume(self, volume: int) -> "TripsPage":
        self.volume_input.fill(str(volume))
        return self

    def fill_loading(self, city: str, suggestion: str) -> "TripsPage":
        self.loading_input.fill(city)
        self.page.get_by_text(suggestion).first.click()
        return self

    def fill_loading_radius(self, radius: int) -> "TripsPage":
        self.loading_radius_input.fill(str(radius))
        return self

    def fill_unloading(self, city: str, suggestion: str) -> "TripsPage":
        self.unloading_input.fill(city)
        self.page.get_by_text(suggestion).first.click()
        return self

    def fill_unloading_radius(self, radius: int) -> "TripsPage":
        self.unloading_radius_input.fill(str(radius))
        return self

    def click_next(self) -> "TripsPage":
        self.next_button.click()
        return self

    def fill_price(self, price) -> "TripsPage":
        self.price_input.fill(str(price))
        return self

    def click_transport_tab(self) -> "TripsPage":
        if self.transport_tab.is_visible():
            self.transport_tab.click()
        return self

    def go_to_trips_list(self) -> "TripsPage":
        self.page.goto(self.LIST_URL, wait_until="domcontentloaded")
        return self

    def create_trip(self, transport: str, volume: int, loading_city: str,
                    loading_suggestion: str, loading_radius: int,
                    unloading_city: str, unloading_suggestion: str,
                    unloading_radius: int, price: int,
                    lifting_capacity: str = "tons") -> "TripsPage":
        self.open_create_trip_form()
        self.accept_cookies_if_visible()
        self.select_transport(transport)
        self.select_lifting_capacity(lifting_capacity)
        self.fill_volume(volume)
        self.fill_loading(loading_city, loading_suggestion)
        self.fill_loading_radius(loading_radius)
        self.fill_unloading(unloading_city, unloading_suggestion)
        self.fill_unloading_radius(unloading_radius)
        self.accept_cookies_if_visible()
        self.click_next()
        self.fill_price(price)
        self.click_next()
        expect(self.page).not_to_have_url(self.CREATE_URL, timeout=15000)
        return self

    def _open_trip_menu(self, index: int = 0) -> "TripsPage":
        """Open 3-dot menu on a trip card. Uses data-testid, falls back to positional."""
        actions = self.page.locator("[data-testid^='trips_trip_actions_button_']")
        if actions.count() > index:
            actions.nth(index).click()
        else:
            self.page.get_by_role("button").nth(4 + index).click()
        return self

    def click_change_on_first_trip(self) -> "TripsPage":
        self._open_trip_menu(0)
        change_item = self.page.get_by_role("menuitem", name="Change")
        expect(change_item).to_be_visible(timeout=5000)
        change_item.click()
        return self

    def edit_trip(self, price) -> "TripsPage":
        self.click_change_on_first_trip()
        self.click_next()
        self.fill_price(price)
        self.click_next()
        return self

    def delete_first_trip(self) -> "TripsPage":
        self._open_trip_menu(0)
        delete_item = self.page.get_by_role("menuitem", name="Delete")
        expect(delete_item).to_be_visible(timeout=5000)
        delete_item.click()
        self.confirm_delete_button.click()
        return self

    def expect_on_trips_page(self) -> "TripsPage":
        expect(self.page).to_have_url(f"{APP_URL}/profile-trips")
        return self

    def expect_trip_in_list(self, price: str, city: str, transport: str) -> "TripsPage":
        self.page.goto(f"{APP_URL}/profile-trips", wait_until="domcontentloaded")
        expect(self.page.get_by_text(price).first).to_be_visible(timeout=10000)
        expect(self.page.get_by_text(city).first).to_be_visible()
        expect(self.page.get_by_text(transport).first).to_be_visible()
        return self
