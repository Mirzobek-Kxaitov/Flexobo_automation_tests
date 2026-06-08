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

    # ── Navigation ──────────────────────────────────────────────

    def go_to_fleet(self):
        self.page.goto(self.FLEET_URL)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)
        return self

    def click_trucks_tab(self):
        self.trucks_tab.click()
        self.page.wait_for_timeout(1000)
        return self

    def click_trailers_tab(self):
        self.trailers_tab.click()
        self.page.wait_for_timeout(1000)
        return self

    # ── Truck CRUD ──────────────────────────────────────────────

    def select_country_option(self, country, search=None):
        self.select_country.click()
        if search:
            self.country_search.fill(search)
            self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=country).click()
        self.page.wait_for_timeout(500)
        return self

    def fill_gov_number(self, gov_number):
        self.gov_number_input.click()
        self.gov_number_input.fill(gov_number)
        return self

    def select_brand(self, brand):
        self.page.get_by_test_id("fleet_brand_select").click()
        self.page.get_by_role("option", name=brand).click()
        self.page.wait_for_timeout(500)
        return self

    def select_year(self, year):
        self.page.get_by_test_id("fleet_year_select").click()
        self.page.get_by_role("option", name=year).click()
        self.page.wait_for_timeout(500)
        return self

    def select_lifting_capacity(self, capacity="tons"):
        self.page.get_by_test_id("fleet_lifting_capacity_select").click()
        self.page.get_by_role("option", name=capacity).click()
        self.page.wait_for_timeout(500)
        return self

    def fill_technical_passport(self, passport):
        self.technical_passport_input.fill(passport)
        return self

    def create_truck(self, country, gov_number, brand, year,
                     lifting_capacity="tons", technical_passport=None,
                     country_search=None):
        self.go_to_fleet()
        self.add_truck_button.click()
        self.page.wait_for_timeout(1000)
        self.select_country_option(country, search=country_search)
        self.fill_gov_number(gov_number)
        self.select_brand(brand)
        self.select_year(year)
        self.select_lifting_capacity(lifting_capacity)
        if technical_passport:
            self.fill_technical_passport(technical_passport)
        self.add_button.click()
        self.page.wait_for_timeout(3000)
        self.go_to_fleet()
        return self

    def _get_truck_row(self, brand, gov_number):
        return self.page.get_by_role("row", name=f"{brand} {gov_number}").first

    def _open_truck_menu(self, brand, gov_number):
        row = self._get_truck_row(brand, gov_number)
        actions = row.locator("[data-testid^='fleet_truck_actions_button_']")
        if actions.count() > 0:
            actions.first.click()
        else:
            row.get_by_role("button").last.click()
        self.page.wait_for_timeout(500)
        return self

    def edit_truck(self, brand, gov_number, new_brand=None):
        self.go_to_fleet()
        self._open_truck_menu(brand, gov_number)
        self.page.get_by_role("menuitem", name="Edit").click()
        self.page.wait_for_timeout(1000)
        if new_brand:
            self.page.get_by_role("combobox").filter(has_text=brand).click()
            self.page.get_by_role("option", name=new_brand).click()
            self.page.wait_for_timeout(500)
        self.save_button.click()
        self.page.wait_for_timeout(2000)
        return self

    def delete_truck(self, brand, gov_number):
        self.go_to_fleet()
        self._get_truck_row(brand, gov_number).wait_for(timeout=15000)
        self._open_truck_menu(brand, gov_number)
        self.page.get_by_role("menuitem", name="Delete").click()
        self.page.wait_for_timeout(500)
        self.confirm_delete_button.click()
        self.page.wait_for_timeout(2000)
        return self

    # ── Trailer CRUD ────────────────────────────────────────────

    def select_trailer_type(self, trailer_type):
        self.page.get_by_test_id("fleet_trailer_type_select").click()
        self.page.get_by_role("option", name=trailer_type).click()
        self.page.wait_for_timeout(500)
        return self

    def fill_dimensions(self, volume=None, length=None, width=None, height=None):
        if volume:
            self.volume_input.fill(str(volume))
        if length:
            self.length_input.fill(str(length))
        if width:
            self.width_input.fill(str(width))
        if height:
            self.height_input.fill(str(height))
        return self

    def select_loading_types(self, loading_type):
        self.page.get_by_test_id("fleet_loading_types_select").click()
        self.page.get_by_role("option", name=loading_type).click()
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)
        return self

    def create_trailer(self, country, gov_number, trailer_type, year,
                       lifting_capacity="tons", volume=None, length=None,
                       width=None, height=None):
        self.go_to_fleet()
        self.click_trailers_tab()
        self.add_trailer_button.click()
        self.page.wait_for_timeout(1000)
        self.select_country_option(country)
        self.fill_gov_number(gov_number)
        self.select_trailer_type(trailer_type)
        self.select_year(year)
        if any([volume, length, width, height]):
            self.fill_dimensions(volume, length, width, height)
        self.select_lifting_capacity(lifting_capacity)
        self.add_button.click()
        self.page.wait_for_timeout(3000)
        return self

    def _get_trailer_row(self, gov_number):
        return self.page.get_by_role("row", name=gov_number).first

    def _open_trailer_menu(self, gov_number):
        row = self._get_trailer_row(gov_number)
        actions = row.locator("[data-testid^='fleet_trailer_actions_button_']")
        if actions.count() > 0:
            actions.first.click()
        else:
            row.get_by_role("button").last.click()
        self.page.wait_for_timeout(500)
        return self

    def edit_trailer(self, gov_number, new_gov_number=None):
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        self.page.get_by_role("menuitem", name="Edit").click()
        self.page.wait_for_timeout(1000)
        if new_gov_number:
            self.gov_number_input.fill(new_gov_number)
        self.save_button.click()
        self.page.wait_for_timeout(2000)
        return self

    def deactivate_trailer(self, gov_number):
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        self.page.get_by_role("menuitem", name="Deactivate").click()
        self.page.wait_for_timeout(500)
        self.confirm_deactivate_button.click()
        self.page.wait_for_timeout(2000)
        return self

    def reactivate_trailer(self, gov_number):
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        self.page.get_by_role("menuitem", name="Reactivate").click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("button", name="Reactivate").click()
        self.page.wait_for_timeout(2000)
        return self

    def delete_trailer(self, gov_number):
        """Delete trailer — must be deactivated first."""
        self.go_to_fleet()
        self.click_trailers_tab()
        self._open_trailer_menu(gov_number)
        self.page.get_by_role("menuitem", name="Delete").click()
        self.page.wait_for_timeout(500)
        self.confirm_deactivate_button.click()
        self.page.wait_for_timeout(2000)
        return self

    # ── Assertions ──────────────────────────────────────────────

    def expect_on_fleet_page(self):
        expect(self.page).to_have_url(re.compile(r"tms/fleet"), timeout=10000)
        return self

    def expect_truck_in_list(self, brand, gov_number):
        expect(self._get_truck_row(brand, gov_number)).to_be_visible(timeout=10000)
        return self

    def expect_truck_not_in_list(self, brand, gov_number):
        expect(self._get_truck_row(brand, gov_number)).not_to_be_visible(timeout=10000)
        return self

    def expect_truck_updated(self):
        expect(self.truck_updated_message).to_be_visible(timeout=10000)
        return self

    def expect_truck_deleted(self):
        expect(self.truck_deleted_message).to_be_visible(timeout=10000)
        return self

    def expect_trailer_in_list(self, gov_number):
        expect(self._get_trailer_row(gov_number)).to_be_visible(timeout=10000)
        return self

    def expect_trailer_not_in_list(self, gov_number):
        expect(self._get_trailer_row(gov_number)).not_to_be_visible(timeout=10000)
        return self

    def expect_trailer_deleted(self):
        expect(self.trailer_deleted_message).to_be_visible(timeout=10000)
        return self
