import os
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")
BASE_URL = os.getenv("BASE_URL")


class ProfilePage:
    def __init__(self, page: Page):
        self.page = page

    #locators
        self.sign_in_text = page.get_by_text("Sign In")
        self.dropdown_menu_trigger = page.get_by_test_id("global_user_menu_button")
        self.profile_item = page.get_by_test_id("sidebar_profile_link")
        self.profile_menu_item = page.get_by_role("menuitem", name="Profile")
        self.my_loads_item = page.get_by_test_id("sidebar_my_loads_link")
        self.my_loads_menu_item = page.get_by_role("menuitem", name="My Loads")
        self.fleet_item = page.get_by_test_id("sidebar_fleet_link")
        self.fleet_menu_item = page.get_by_role("menuitem", name="Fleet")
        self.my_trips_item = page.get_by_test_id("sidebar_my_trips_link")
        self.my_trips_menu_item = page.get_by_role("menuitem", name="My trips")
        self.logout_item = page.get_by_test_id("global_logout_menu_item")
        self.confirm_yes_button = page.get_by_test_id("global_logout_confirm_button")
    
    def open_menu(self):
        self.dropdown_menu_trigger.click()
        return self

    def _click_sidebar_or_menu(self, sidebar_item, menu_item):
        if sidebar_item.is_visible():
            sidebar_item.click()
        else:
            self.open_menu()
            menu_item.click()
        return self
    
    def go_to_profile(self):
        return self._click_sidebar_or_menu(self.profile_item, self.profile_menu_item)
    
    def go_to_my_loads(self):
        return self._click_sidebar_or_menu(self.my_loads_item, self.my_loads_menu_item)
    
    def go_to_fleet(self):
        return self._click_sidebar_or_menu(self.fleet_item, self.fleet_menu_item)
    
    def go_to_my_trips(self):
        return self._click_sidebar_or_menu(self.my_trips_item, self.my_trips_menu_item)
    
    def logout(self):
        self.open_menu()
        self.logout_item.click()
        self.confirm_yes_button.click()
        return self
    

    def expect_on_profile_page(self):
        expect(self.page).to_have_url(f"{APP_URL}/profile/root")
        return self

    def expect_on_my_loads_page(self):
        expect(self.page).to_have_url(f"{APP_URL}/profile-load")
        return self

    def expect_on_fleet_page(self):
        expect(self.page).to_have_url(f"{APP_URL}/tms/fleet")
        return self

    def expect_on_my_trips_page(self):
        expect(self.page).to_have_url(f"{APP_URL}/profile-trips")
        return self

    def expect_logged_out(self):
        import re
        expect(self.page).to_have_url(re.compile(r"sign-in|landing"))
        return self
