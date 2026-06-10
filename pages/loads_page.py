import os
import re
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")


class LoadsPage:
    def __init__(self, page: Page):
        self.page = page

        #locators
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

    def toggle_in_contract_filter(self):
        self.in_contract_filter.click()
        return self
    
    def toggle_in_transit_filter(self):
        self.in_transit_filter.click()
        return self
    
    def toggle_delivered_filter(self):
        self.delivered_filter.click()
        return self 
    
    def open_create_load_form(self):
        self.page.goto(f"{APP_URL}/loads")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.add_button.click()
        self.load_menu_item.click()
        return self
    
    def fill_from(self, city_name, suggestion_text):
        self.from_input.fill(city_name)
        self.page.get_by_text(suggestion_text).click()
        return self
    
    def fill_to(self, city_name, suggestion_text):
        self.to_input.fill(city_name)
        self.page.get_by_text(suggestion_text).click()
        return self
    
    def select_load_type(self, type_name):
        self.load_type_button.click()
        self.page.get_by_text(type_name).click()
        return self
    
    def fill_weight(self, weight):
        self.weight_input.fill(weight)
        return self

    def pick_loading_date(self):
        self.date_button.click()
        self.next_month_button.click()
        self.page.wait_for_timeout(300)
        # Select first available day in next month
        self.page.locator(
            "td[role='gridcell']:not([data-outside='true']) button:not([disabled])"
        ).first.click()
        self.page.wait_for_timeout(300)
        return self

    def accept_cookies_if_visible(self):
        if self.cookie_accept_button.is_visible():
            self.cookie_accept_button.click()
        return self
    
    def click_next(self):
        self.next_button.click()
        return self 
    
    def select_body_type(self, body_type):
        self.body_type_button.click()
        self.page.get_by_role("option", name=body_type).click()
        return self

    def select_loading_type(self, loading_type):
        self.page.get_by_test_id("loads_loading_type_select").or_(
            self.page.get_by_role("combobox").filter(has_text=re.compile(r"^Loading type$"))
        ).first.click()
        self.page.get_by_role("option", name=loading_type).click()
        return self

    def select_unloading_type(self, unloading_type):
        self.page.get_by_test_id("loads_unloading_type_select").or_(
            self.page.get_by_role("combobox").filter(has_text=re.compile(r"^Unloading type$"))
        ).first.click()
        self.page.get_by_role("option", name=unloading_type).click()
        return self
    
    def fill_price(self, price):
        self.price_input.fill(price)
        return self
    
    def publish(self):
        self.publish_button.click()
        return self 
    

    
    def create_load(self, from_city, from_suggestion, to_city, to_suggestion,
                    load_type, weight, body_type, price):
        """Create load — 2025-06 form layout:
        Step 1: Route + load type + weight + date
        Step 2: Body (transport type)
        Step 3: Payment (price)
        Step 4: Publish
        """
        self.open_create_load_form()
        expect(self.from_input).to_be_visible(timeout=15000)

        # Step 1 — Route & load
        self.fill_from(from_city, from_suggestion)
        self.fill_to(to_city, to_suggestion)
        self.select_load_type(load_type)
        self.fill_weight(weight)
        self.pick_loading_date()
        self.accept_cookies_if_visible()
        self.click_next()

        # Step 2 — Body
        expect(self.body_type_button).to_be_visible(timeout=10000)
        self.select_body_type(body_type)
        self.click_next()

        # Step 3 — Payment
        expect(self.price_input).to_be_visible(timeout=10000)
        self.fill_price(price)
        self.click_next()

        # Step 4 — Publish
        if self.publish_button.is_visible(timeout=5000):
            self.publish()
        self.page.wait_for_timeout(3000)
        return self
    
    def _open_load_menu(self, index=0):
        """Open the 3-dot dropdown menu on a load card by index."""
        actions = self.page.locator("[data-testid^='loads_load_actions_button_']")
        if actions.count() > index:
            actions.nth(index).click()
        else:
            # Fallback: testid bo'lmaganda pozitsion selektor (frontend'ga testid qo'shilganda o'chirish)
            self.page.get_by_role("button").nth(4 + index).click()
        self.page.wait_for_timeout(500)
        return self

    def click_change_on_first_load(self):
        self._open_load_menu(0)
        self.page.get_by_role("menuitem", name="Change").click()
        self.page.wait_for_timeout(2000)
        return self

    def delete_first_load(self):
        """Delete the first load via 3-dot menu."""
        self._open_load_menu(0)
        self.page.get_by_role("menuitem", name="Delete").click()
        self.page.wait_for_timeout(1000)
        self.confirm_delete_button.click()
        self.page.wait_for_timeout(2000)
        return self
    
    def change_load_type(self, current_type, new_type):
        """Edit sahifasida load type o'zgartirish (hozirgi qiymat ko'rsatilgan)"""
        self.page.locator(f"button:has-text('{current_type}')").click()
        self.page.get_by_role("option", name=new_type).click()
        return self

    def edit_load(self, from_city, from_suggestion, to_city, to_suggestion,
                  weight, price):
        """Birinchi yukni tahrirlaydi — faqat o'zgaradigan maydonlar"""
        self.click_change_on_first_load()
        self.fill_from(from_city, from_suggestion)
        self.fill_to(to_city, to_suggestion)
        self.fill_weight(weight)
        self.accept_cookies_if_visible()
        self.click_next()
        # Step 2 (Body) — tegmaymiz, avvalgi qiymat qoladi
        self.click_next()
        # Step 3 (Payment)
        self.fill_price(price)
        self.click_next()
        # Step 4 (Confirmation)
        self.publish()
        return self




    def expect_on_body_step(self):
        expect(self.body_step_heading).to_be_visible()
        return self
    
    def expect_on_payment_step(self):
        expect(self.payment_step_heading).to_be_visible()
        return self
    
    def expect_load_created(self):
        expect(self.page).not_to_have_url(re.compile(r".*/create.*"), timeout=10000)
        return self

    def expect_on_loads_page(self):
        expect(self.page).to_have_url(re.compile(r"profile-load|profile/root"), timeout=10000)
        return self
    
    def expect_in_contract_checked(self):
        expect(self.in_contract_filter).to_have_attribute("data-state", "checked")
        return self
    
    def expect_in_transit_checked(self):
        expect(self.in_transit_filter).to_have_attribute("data-state", "checked")
        return self
    
    def expect_delivered_checked(self):
        expect(self.delivered_filter).to_have_attribute("data-state", "checked")
        return self 
    
