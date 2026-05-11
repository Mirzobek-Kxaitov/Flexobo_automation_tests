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
        
        self.cookie_accept_button = self.page.get_by_role("button", name="Accept")

        self.transport_combobox = page.get_by_role("combobox").first
        self.unit_combobox = page.get_by_role("combobox").filter(has_text="Choose")
        self.volume_input = page.get_by_role("textbox", name="Volume*")
        self.loading_input = page.get_by_role("textbox", name="Loading", exact=True)
        self.loading_radius_input = page.get_by_role("textbox", name="Loading radius", exact=True)
        self.unloading_input = page.get_by_role("textbox", name="Unloading", exact=True)
        self.unloading_radius_input = page.get_by_role("textbox", name="Unloading radius")

        self.price_input = page.get_by_role("textbox", name="Price*")

        self.transport_tab = self.page.get_by_role("tab", name="Transport")

        self.next_button = self.page.get_by_role("button", name="Next")

        # Edit/Delete locators (Trips ro'yxat sahifasida)
        self.change_button = page.get_by_role("button", name="Change").first
        self.delete_button = page.locator("button:has(svg path[d^='M19.5 5.5'])").first
        self.confirm_delete_button = page.get_by_role("button", name="Delete", exact=True)


    def open_create_trip_form(self):
        self.page.goto(self.CREATE_URL)
        return self
    
    def accept_cookies_if_visible(self):
        if self.cookie_accept_button.is_visible():
            self.cookie_accept_button.click()
        return self
    
    def select_transport(self, name):
        self.transport_combobox.click()
        self.page.get_by_role("option", name=name).click()
        return self
    
    def select_unit_kg(self):
        self.page.get_by_role("combobox").filter(has_text="Choose").click()
        self.page.get_by_text("12 tons").click()
        return self
    

    def fill_volume(self, volume):
        self.volume_input.fill(str(volume))
        return self
    
    def fill_loading(self, city,suggestion):
        self.loading_input.fill(city)
        self.page.get_by_text(suggestion).first.click()
        return self
    
    def fill_loading_radius(self, radius):
        self.loading_radius_input.fill(str(radius))
        return self     
    
    def fill_unloading(self, city, suggestion):
        self.unloading_input.fill(city)
        self.page.get_by_text(suggestion).first.click()
        return self
    
    def fill_unloading_radius(self,radius):
        self.unloading_radius_input.fill(str(radius))
        return self

    def click_next(self):
        self.next_button.click()
        return self

    def fill_price(self, price):
        self.price_input.fill(str(price))
        return self

    def click_transport_tab(self):
        # Broker'da success ekranda "Transport" tab bor — bosamiz.
        # Carrier/OwnerOperator'da yo'q (avto-redirect) — o'tkazib yuboramiz.
        if self.transport_tab.is_visible():
            self.transport_tab.click()
        return self

    def go_to_trips_list(self):
        self.page.goto(self.LIST_URL)
        return self
    

    def create_trip(self, transport, volume, loading_city, loading_suggestion,
                    loading_radius, unloading_city, unloading_suggestion,
                    unloading_radius, price):
        self.open_create_trip_form()
        self.accept_cookies_if_visible()
        self.select_transport(transport)
        self.select_unit_kg()
        self.fill_volume(volume)
        self.fill_loading(loading_city, loading_suggestion)
        self.fill_loading_radius(loading_radius)
        self.fill_unloading(unloading_city, unloading_suggestion)
        self.fill_unloading_radius(unloading_radius)
        self.click_next()
        self.fill_price(price)
        self.click_next()
        self.click_transport_tab()
        self.go_to_trips_list()
        return self

    def click_change_on_first_trip(self):
        self.change_button.wait_for(state="visible", timeout=15000)
        self.change_button.click()
        return self

    def edit_trip(self, price):
        """Birinchi safarni tahrirlaydi — faqat narxni o'zgartiradi"""
        self.click_change_on_first_trip()
        self.click_next()
        self.fill_price(price)
        self.click_next()
        return self

    def delete_first_trip(self):
        """Birinchi safarni o'chiradi (Delete → Confirm)"""
        self.delete_button.click()
        self.confirm_delete_button.click()
        return self

    def expect_on_trips_page(self):
        expect(self.page).to_have_url(f"{APP_URL}/profile-trips")
        return self

    def expect_trip_in_list(self, price, city, transport):
        expect(self.page.get_by_text(price).first).to_be_visible()
        expect(self.page.get_by_text(city).first).to_be_visible()
        expect(self.page.get_by_text(transport).first).to_be_visible()
        expect(self.page.get_by_text("New").first).to_be_visible()
        return self
