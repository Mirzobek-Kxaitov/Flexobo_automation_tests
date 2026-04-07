from playwright.sync_api import Page, expect

def open_menu(page: Page):
    """Dropdown menyu ochish"""
    page.get_by_text("Sign In").click()
    page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()

def test_open_profile_page(logged_in: Page):
    page = logged_in
    open_menu(page)
    page.get_by_role("menuitem", name="Profile").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/profile/root")

def test_my_loads_page(logged_in: Page):
    page = logged_in
    open_menu(page)
    page.get_by_role("menuitem", name="My Loads").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")

def test_my_trucks_page(logged_in: Page):
    page = logged_in
    open_menu(page)
    page.get_by_role("menuitem", name="Fleet").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/tms/fleet")

def test_my_trips_page(logged_in: Page):
    page = logged_in
    open_menu(page)
    page.get_by_role("menuitem", name="My trips").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/profile-trips")

def test_user_can_logout(logged_in: Page):
    page = logged_in
    accept_button = page.get_by_role("button", name="Accept")
    if accept_button.is_visible():
        accept_button.click()
    open_menu(page)
    page.get_by_role("menuitem", name="Logout").click()
    page.get_by_text("Yes").click()
    expect(page).to_have_url("https://landing-dev.flexobo.com/", timeout=10000)
