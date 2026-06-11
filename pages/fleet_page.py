import os
import re
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")


class FleetPage:

    FLEET_URL = f"{APP_URL}/tms/fleet"

    def __init__(self, page: Page):
        self.page = page

        # Tabs
        self.trucks_tab = page.get_by_test_id("fleet_trucks_tab")
        self.trailers_tab = page.get_by_test_id("fleet_trailers_tab")

        # Truck form
        self.add_truck_button = page.get_by_test_id("fleet_add_truck_button")
        self.select_country = page.get_by_test_id("fleet_country_select")
        self.country_search = (
            page.get_by_test_id("fleet_country_search_input")
            .or_(page.get_by_placeholder("Search country..."))
            .first
        )
        self.gov_number_input = page.get_by_test_id("fleet_gov_number_input")
        self.technical_passport_input = page.get_by_test_id("fleet_technical_passport_input")
        self.add_button = page.get_by_test_id("fleet_form_submit_button")
        self.save_button = (
            page.get_by_test_id("fleet_form_submit_button")
            .or_(page.get_by_role("button", name="Save"))
            .first
        )

        # Trailer form
        self.add_trailer_button = page.get_by_test_id("fleet_add_trailer_button")
        self.volume_input = page.get_by_test_id("fleet_volume_input")
        self.length_input = page.get_by_test_id("fleet_length_input")
        self.width_input = page.get_by_test_id("fleet_width_input")
        self.height_input = page.get_by_test_id("fleet_height_input")

        # Confirm dialogs
        self.confirm_delete_button = (
            page.get_by_test_id("fleet_delete_confirm_button")
            .or_(page.get_by_role("button", name="Delete"))
            .first
        )
        self.confirm_deactivate_button = (
            page.get_by_test_id("fleet_deactivate_confirm_button")
            .or_(page.get_by_role("button", name="Deactivate"))
            .first
        )
        self.confirm_detach_trailer_button = page.get_by_test_id("fleet_detach_trailer_confirm_button")
        self.confirm_detach_driver_button = page.get_by_test_id("fleet_detach_driver_confirm_button")
        self.cancel_button = page.get_by_test_id("fleet_form_cancel_button")

        # Success messages
        self.truck_updated_message = (
            page.get_by_test_id("fleet_success_message")
            .or_(page.get_by_text("Truck updated successfully"))
            .first
        )
        self.truck_deleted_message = page.get_by_text("Transport deleted successfully")
        self.trailer_deleted_message = page.get_by_text("Trailer deleted successfully")
        self.trailer_detached_message = page.get_by_text("Trailer detached successfully")

    # ── Navigation ──

    def go_to_fleet(self) -> "FleetPage":
        self.page.goto(self.FLEET_URL, wait_until="domcontentloaded")
        expect(self.trucks_tab).to_be_visible()
        return self

    def click_trucks_tab(self) -> "FleetPage":
        self.trucks_tab.click()
        return self

    def click_trailers_tab(self) -> "FleetPage":
        self.trailers_tab.click()
        expect(self.add_trailer_button).to_be_visible()
        return self

    # ── Truck CRUD ──

    def select_country_option(self, country: str, search: str = None) -> "FleetPage":
        self.select_country.click()
        if search:
            self.country_search.fill(search)
        option = self.page.get_by_role("option", name=country)
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_gov_number(self, gov_number: str) -> "FleetPage":
        self.gov_number_input.click()
        self.gov_number_input.fill(gov_number)
        return self

    def select_brand(self, brand: str) -> "FleetPage":
        self.page.get_by_test_id("fleet_brand_select").click()
        option = self.page.get_by_role("option", name=brand)
        expect(option).to_be_visible()
        option.click()
        return self

    def select_year(self, year: str) -> "FleetPage":
        self.page.get_by_test_id("fleet_year_select").click()
        option = self.page.get_by_role("option", name=year)
        expect(option).to_be_visible()
        option.click()
        return self

    def select_lifting_capacity(self, capacity: str = "tons") -> "FleetPage":
        self.page.get_by_test_id("fleet_lifting_capacity_select").click()
        option = self.page.get_by_role("option", name=capacity)
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_technical_passport(self, passport: str) -> "FleetPage":
        self.technical_passport_input.fill(passport)
        return self

    def create_truck(self, country: str, gov_number: str, brand: str, year: str,
                     lifting_capacity: str = "tons", technical_passport: str = None,
                     country_search: str = None) -> "FleetPage":
        self.go_to_fleet()
        self.add_truck_button.click()
        expect(self.select_country).to_be_visible()
        self.select_country_option(country, search=country_search)
        self.fill_gov_number(gov_number)
        self.select_brand(brand)
        self.select_year(year)
        self.select_lifting_capacity(lifting_capacity)
        if technical_passport:
            self.fill_technical_passport(technical_passport)
        self.add_button.click()
        expect(self.page).to_have_url(re.compile(r"tms/fleet"))
        return self

    def _get_truck_row(self, brand: str, gov_number: str):
        return self.page.get_by_role("row", name=f"{brand} {gov_number}").first

    def _open_truck_menu(self, brand: str, gov_number: str) -> "FleetPage":
        row = self._get_truck_row(brand, gov_number)
        actions = row.locator("[data-testid^='fleet_truck_actions_button_']")
        if actions.count() > 0:
            actions.first.click()
        else:
            row.get_by_role("button").last.click()
        return self

    def edit_truck(self, brand: str, gov_number: str, new_brand: str = None) -> "FleetPage":
        self.go_to_fleet()
        self._open_truck_menu(brand, gov_number)
        edit_item = self.page.get_by_role("menuitem", name="Edit")
        expect(edit_item).to_be_visible()
        edit_item.click()
        if new_brand:
            self.page.get_by_role("combobox").filter(has_text=brand).click()
            option = self.page.get_by_role("option", name=new_brand)
            expect(option).to_be_visible()
            option.click()
        self.save_button.click()
        expect(self.truck_updated_message).to_be_visible()
        return self

    def delete_truck(self, brand: str, gov_number: str) -> "FleetPage":
        self.go_to_fleet()
        expect(self._get_truck_row(brand, gov_number)).to_be_visible()
        self._open_truck_menu(brand, gov_number)
        delete_item = self.page.get_by_role("menuitem", name="Delete")
        expect(delete_item).to_be_visible()
        delete_item.click()
        self.confirm_delete_button.click()
        return self

    # ── Trailer CRUD ──

    def select_trailer_type(self, trailer_type: str) -> "FleetPage":
        self.page.get_by_test_id("fleet_trailer_type_select").click()
        option = self.page.get_by_role("option", name=trailer_type)
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_dimensions(self, volume: int = None, length: int = None,
                        width: int = None, height: int = None) -> "FleetPage":
        if volume:
            self.volume_input.fill(str(volume))
        if length:
            self.length_input.fill(str(length))
        if width:
            self.width_input.fill(str(width))
        if height:
            self.height_input.fill(str(height))
        return self

    def select_loading_types(self, loading_type: str) -> "FleetPage":
        self.page.get_by_test_id("fleet_loading_types_select").click()
        option = self.page.get_by_role("option", name=loading_type)
        expect(option).to_be_visible()
        option.click()
        self.page.keyboard.press("Escape")
        return self

    def create_trailer(self, country: str, gov_number: str, trailer_type: str,
                       year: str, lifting_capacity: str = "tons",
                       volume: int = None, length: int = None,
                       width: int = None, height: int = None) -> "FleetPage":
        self.go_to_fleet()
        self.click_trailers_tab()
        self.add_trailer_button.click()
        expect(self.select_country).to_be_visible()
        self.select_country_option(country)
        self.fill_gov_number(gov_number)
        self.select_trailer_type(trailer_type)
        self.select_year(year)
        if any([volume, length, width, height]):
            self.fill_dimensions(volume, length, width, height)
        self.select_lifting_capacity(lifting_capacity)
        self.add_button.click()
        expect(self.page).to_have_url(re.compile(r"tms/fleet"))
        return self

    def _get_trailer_row(self, gov_number: str):
        return self.page.get_by_role("row", name=gov_number).first

    def _open_trailer_menu(self, gov_number: str) -> "FleetPage":
        row = self._get_trailer_row(gov_number)
        actions = row.locator("[data-testid^='fleet_trailer_actions_button_']")
        if actions.count() > 0:
            actions.first.click()
        else:
            row.get_by_role("button").last.click()
        return self

    def edit_trailer(self, gov_number: str, new_gov_number: str = None) -> "FleetPage":
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        edit_item = self.page.get_by_role("menuitem", name="Edit")
        expect(edit_item).to_be_visible()
        edit_item.click()
        if new_gov_number:
            self.gov_number_input.fill(new_gov_number)
        self.save_button.click()
        return self

    def deactivate_trailer(self, gov_number: str) -> "FleetPage":
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        deactivate_item = self.page.get_by_role("menuitem", name="Deactivate")
        expect(deactivate_item).to_be_visible()
        deactivate_item.click()
        self.confirm_deactivate_button.click()
        return self

    def reactivate_trailer(self, gov_number: str) -> "FleetPage":
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        reactivate_item = self.page.get_by_role("menuitem", name="Reactivate")
        expect(reactivate_item).to_be_visible()
        reactivate_item.click()
        self.page.get_by_role("button", name="Reactivate").click()
        return self

    def delete_trailer(self, gov_number: str) -> "FleetPage":
        """Delete trailer — must be deactivated first."""
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        delete_item = self.page.get_by_role("menuitem", name="Delete")
        expect(delete_item).to_be_visible()
        delete_item.click()
        self.confirm_delete_button.click()
        return self

    # ── Assertions ──

    def expect_on_fleet_page(self) -> "FleetPage":
        expect(self.page).to_have_url(re.compile(r"tms/fleet"))
        return self

    def expect_truck_in_list(self, brand: str, gov_number: str) -> "FleetPage":
        expect(self._get_truck_row(brand, gov_number)).to_be_visible()
        return self

    def expect_truck_not_in_list(self, brand: str, gov_number: str) -> "FleetPage":
        expect(self._get_truck_row(brand, gov_number)).not_to_be_visible()
        return self

    def expect_truck_updated(self) -> "FleetPage":
        expect(self.truck_updated_message).to_be_visible()
        return self

    def expect_truck_deleted(self) -> "FleetPage":
        expect(self.truck_deleted_message).to_be_visible()
        return self

    def expect_trailer_in_list(self, gov_number: str) -> "FleetPage":
        expect(self._get_trailer_row(gov_number)).to_be_visible()
        return self

    def expect_trailer_not_in_list(self, gov_number: str) -> "FleetPage":
        expect(self._get_trailer_row(gov_number)).not_to_be_visible()
        return self

    def expect_trailer_deleted(self) -> "FleetPage":
        expect(self.trailer_deleted_message).to_be_visible()
        return self
