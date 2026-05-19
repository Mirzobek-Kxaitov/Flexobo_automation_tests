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
        
        self.add_button = page.get_by_role("button", name="Add")    
        self.load_menu_item = page.get_by_role("menuitem", name="Load")
          
        self.from_input = page.get_by_placeholder("From")
        self.to_input = page.get_by_placeholder("To")
        self.load_type_button = page.locator("button:has-text('Load type')")
        self.weight_input = page.get_by_placeholder("Load weight")
        self.date_button = page.get_by_role("button", name="Date")
        self.next_month_button = page.get_by_role("button", name="Next month")
        self.cookie_accept_button = page.get_by_role("button", name="Accept")

        self.body_type_button = page.locator("button:has-text('Transport type')")
        self.body_step_heading = page.get_by_text("Body", exact=True)

        self.price_input = page.get_by_placeholder("Price")
        self.payment_step_heading = page.get_by_text("Payment", exact=True)

        self.next_button = page.get_by_role("button", name="Next", exact=True)
        self.publish_button = page.get_by_role("button", name="Publish", exact=True)
        self.success_message = page.get_by_text("Load created successfully")
        self.confirm_delete_button = page.get_by_role("button", name="Delete", exact=True)

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
        self.page.get_by_role("combobox").filter(has_text="Transport type").click()
        self.page.get_by_role("option", name=body_type).click()
        return self

    def select_loading_type(self, loading_type):
        self.page.get_by_role("combobox").filter(has_text=re.compile(r"^Loading type$")).click()
        self.page.get_by_role("option", name=loading_type).click()
        return self

    def select_unloading_type(self, unloading_type):
        self.page.get_by_role("combobox").filter(has_text=re.compile(r"^Unloading type$")).click()
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
        self.open_create_load_form()
        self.fill_from(from_city, from_suggestion)
        self.fill_to(to_city, to_suggestion)
        self.select_load_type(load_type)
        self.pick_loading_date()
        self.accept_cookies_if_visible()
        self.click_next()
        self.fill_weight(weight)
        self.click_next()
        # Skip optional step
        self.click_next()
        self.select_body_type(body_type)
        self.click_next()
        self.fill_price(price)
        self.click_next()
        self.page.wait_for_timeout(2000)
        self.publish()
        return self
    
    def _open_load_menu(self, index=0):
        """Open the 3-dot dropdown menu on a load card by index."""
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
    
