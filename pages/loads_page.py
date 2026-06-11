import os
import re
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")


class LoadsPage:
    def __init__(self, page: Page):
        self.page = page

        self.in_contract_filter = page.locator("button[value='in_contract']")
        self.in_transit_filter = page.locator("button[value='in_transit']")
        self.delivered_filter = page.locator("button[value='delivered']")
        self.my_loads_heading = page.get_by_role("heading", name="My loads")

        self.add_button = page.get_by_test_id("global_add_button")
        self.load_menu_item = page.get_by_test_id("global_add_load_menu_item")

        self.from_input = page.get_by_test_id("loads_from_input")
        self.to_input = page.get_by_test_id("loads_to_input")
        self.load_type_button = page.get_by_test_id("loads_load_type_select")
        self.weight_input = page.get_by_test_id("loads_weight_input")
        self.date_button = page.get_by_test_id("loads_date_button")
        self.next_month_button = (
            page.get_by_test_id("calendar_next_month_button")
            .or_(page.get_by_role("button", name="Next month"))
            .first
        )
        self.cookie_accept_button = page.get_by_test_id("global_cookie_accept_button")

        self.body_type_button = (
            page.get_by_test_id("loads_transport_type_select")
            .or_(page.locator("button:has-text('Transport type')"))
            .first
        )
        self.body_step_heading = (
            page.get_by_test_id("loads_body_step")
            .or_(page.get_by_text("Body", exact=True))
            .first
        )

        self.price_input = page.get_by_test_id("loads_price_input")
        self.payment_step_heading = (
            page.get_by_test_id("loads_payment_step")
            .or_(page.get_by_text("Payment", exact=True))
            .first
        )

        self.next_button = page.get_by_test_id("loads_next_button")
        self.publish_button = page.get_by_test_id("loads_publish_button")
        self.success_message = (
            page.get_by_test_id("loads_success_message")
            .or_(page.get_by_text("Load created successfully"))
            .first
        )
        self.confirm_delete_button = page.get_by_test_id("loads_delete_confirm_button")

    def toggle_in_contract_filter(self) -> "LoadsPage":
        self.in_contract_filter.click()
        return self

    def toggle_in_transit_filter(self) -> "LoadsPage":
        self.in_transit_filter.click()
        return self

    def toggle_delivered_filter(self) -> "LoadsPage":
        self.delivered_filter.click()
        return self

    def open_create_load_form(self) -> "LoadsPage":
        self.page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")
        expect(self.add_button).to_be_visible()
        self.add_button.click()
        self.load_menu_item.click()
        return self

    def fill_from(self, city_name: str, suggestion_text: str) -> "LoadsPage":
        self.from_input.fill(city_name)
        self.page.get_by_text(suggestion_text).click()
        return self

    def fill_to(self, city_name: str, suggestion_text: str) -> "LoadsPage":
        self.to_input.fill(city_name)
        self.page.get_by_text(suggestion_text).click()
        return self

    def select_load_type(self, type_name: str) -> "LoadsPage":
        self.load_type_button.click()
        self.page.get_by_text(type_name).click()
        return self

    def fill_weight(self, weight: str) -> "LoadsPage":
        self.weight_input.fill(weight)
        return self

    def pick_loading_date(self) -> "LoadsPage":
        self.date_button.click()
        self.next_month_button.click()
        day_cell = self.page.locator(
            "td[role='gridcell']:not([data-outside='true']) button:not([disabled])"
        ).first
        expect(day_cell).to_be_visible()
        day_cell.click()
        return self

    def accept_cookies_if_visible(self) -> "LoadsPage":
        if self.cookie_accept_button.is_visible():
            self.cookie_accept_button.click()
        return self

    def click_next(self) -> "LoadsPage":
        self.next_button.click()
        return self

    def select_body_type(self, body_type: str) -> "LoadsPage":
        self.body_type_button.click()
        self.page.get_by_role("option", name=body_type).click()
        return self

    def select_loading_type(self, loading_type: str) -> "LoadsPage":
        self.page.get_by_test_id("loads_loading_type_select").or_(
            self.page.get_by_role("combobox").filter(has_text=re.compile(r"^Loading type$"))
        ).first.click()
        self.page.get_by_role("option", name=loading_type).click()
        return self

    def select_unloading_type(self, unloading_type: str) -> "LoadsPage":
        self.page.get_by_test_id("loads_unloading_type_select").or_(
            self.page.get_by_role("combobox").filter(has_text=re.compile(r"^Unloading type$"))
        ).first.click()
        self.page.get_by_role("option", name=unloading_type).click()
        return self

    def fill_price(self, price: str) -> "LoadsPage":
        self.price_input.fill(price)
        return self

    def publish(self) -> "LoadsPage":
        self.publish_button.click()
        return self

    def create_load(self, from_city: str, from_suggestion: str, to_city: str,
                    to_suggestion: str, load_type: str, weight: str,
                    body_type: str, price: str) -> "LoadsPage":
        """Create load via 4-step form."""
        self.open_create_load_form()
        expect(self.from_input).to_be_visible()

        self.fill_from(from_city, from_suggestion)
        self.fill_to(to_city, to_suggestion)
        self.select_load_type(load_type)
        self.fill_weight(weight)
        self.pick_loading_date()
        self.accept_cookies_if_visible()
        self.click_next()

        expect(self.body_type_button).to_be_visible()
        self.select_body_type(body_type)
        self.click_next()

        expect(self.price_input).to_be_visible()
        self.fill_price(price)
        self.click_next()

        if self.publish_button.is_visible():
            self.publish()
        expect(self.page).not_to_have_url(re.compile(r".*/create.*"))
        return self

    def _open_load_menu(self, index: int = 0) -> "LoadsPage":
        """Open 3-dot menu on a load card. Uses data-testid, falls back to positional."""
        actions = self.page.locator("[data-testid^='loads_load_actions_button_']")
        if actions.count() > index:
            actions.nth(index).click()
        else:
            self.page.get_by_role("button").nth(4 + index).click()
        return self

    def click_change_on_first_load(self) -> "LoadsPage":
        self._open_load_menu(0)
        change_item = self.page.get_by_role("menuitem", name="Change")
        expect(change_item).to_be_visible()
        change_item.click()
        return self

    def delete_first_load(self) -> "LoadsPage":
        self._open_load_menu(0)
        delete_item = self.page.get_by_role("menuitem", name="Delete")
        expect(delete_item).to_be_visible()
        delete_item.click()
        self.confirm_delete_button.click()
        return self

    def change_load_type(self, current_type: str, new_type: str) -> "LoadsPage":
        self.page.locator(f"button:has-text('{current_type}')").click()
        self.page.get_by_role("option", name=new_type).click()
        return self

    def edit_load(self, from_city: str, from_suggestion: str, to_city: str,
                  to_suggestion: str, weight: str, price: str) -> "LoadsPage":
        self.click_change_on_first_load()
        self.fill_from(from_city, from_suggestion)
        self.fill_to(to_city, to_suggestion)
        self.fill_weight(weight)
        self.accept_cookies_if_visible()
        self.click_next()
        self.click_next()
        self.fill_price(price)
        self.click_next()
        self.publish()
        return self

    def expect_on_body_step(self) -> "LoadsPage":
        expect(self.body_step_heading).to_be_visible()
        return self

    def expect_on_payment_step(self) -> "LoadsPage":
        expect(self.payment_step_heading).to_be_visible()
        return self

    def expect_load_created(self) -> "LoadsPage":
        expect(self.page).not_to_have_url(re.compile(r".*/create.*"))
        return self

    def expect_on_loads_page(self) -> "LoadsPage":
        expect(self.page).to_have_url(re.compile(r"profile-load|profile/root"))
        return self

    def expect_in_contract_checked(self) -> "LoadsPage":
        expect(self.in_contract_filter).to_have_attribute("data-state", "checked")
        return self

    def expect_in_transit_checked(self) -> "LoadsPage":
        expect(self.in_transit_filter).to_have_attribute("data-state", "checked")
        return self

    def expect_delivered_checked(self) -> "LoadsPage":
        expect(self.delivered_filter).to_have_attribute("data-state", "checked")
        return self
