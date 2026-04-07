from playwright.sync_api import Page, expect

def test_create_load(logged_in: Page):
    """Create a load by filling out the form and submitting it"""
    page = logged_in
    page.get_by_role("button", name="Add").click()
    page.get_by_role("menuitem", name="Load").click()
    
# Place FROM
    page.get_by_placeholder("From").fill("Toshkent")
    page.get_by_text("Tashkent, 100000, Uzbekistan").click()
# Place TO  
    page.get_by_placeholder("To").fill("Termez")
    page.get_by_text("Termez, Termiz District, Surxondaryo Province, Uzbekistan").first.click()
# Load type dropdown
    page.locator("button:has-text('Load type')").click()
    page.get_by_text("Metal aggregate").click()
#Load weight field
    page.get_by_placeholder("Load weight").fill("20")
# Loading date calendar
    page.get_by_role("button", name="Date").click()
    page.get_by_role("button", name="Next month").click()
    page.get_by_role("gridcell", name="15").click()
# Coockie accept
    accept_button = page.get_by_role("button", name="Accept")
    if accept_button.is_visible():
        accept_button.click()
#next page
    page.get_by_role("button", name="Next", exact=True).click()
    expect(page.get_by_text("Body", exact=True)).to_be_visible()
    # Step 2 - Body
    expect(page.get_by_text("Body", exact=True)).to_be_visible()
# Body type dropdown
    page.locator("button:has-text('Body type')").click() 
    page.get_by_role("option", name="Mega truck").click()  
# Next
    page.get_by_role("button", name="Next", exact=True).click()
    # Step 3 - Payment
    expect(page.get_by_text("Payment", exact=True)).to_be_visible()
    page.get_by_placeholder("Price").fill("1000")  # ✅
    page.get_by_role("button", name="Next", exact=True).click()
# Step 4 - Confirmation
    page.get_by_role("button", name="Publish").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/loads")
    expect(page.get_by_text("Load created successfully")).to_be_visible()

def test_loads_page_is_accessible(logged_in: Page):
    """Check if the loads page is accessible after logging in"""
    page = logged_in
    page.get_by_text("Sign In").click()
    page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
    page.get_by_role("menuitem", name="My Loads").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
    expect(page.get_by_text("My Loads")).to_be_visible()

def test_in_contract_filter_on_loads_page(logged_in: Page):
    """Check if the 'In Contract' filter on the loads page can be toggled"""
    page = logged_in
    page.get_by_text("Sign In").click()
    page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
    page.get_by_role("menuitem", name="My Loads").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
    in_contract_filter = page.locator("button[value='in_contract']")
    in_contract_filter.click()
    expect(in_contract_filter).to_have_attribute("data-state", "checked")

def test_in_transit_filter_on_loads_page(logged_in: Page):
    """Check if the 'In Transit' filter on the loads page can be toggled"""
    page = logged_in        
    page.get_by_text("Sign In").click()
    page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
    page.get_by_role("menuitem", name="My Loads").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
    in_transit_filter = page.locator("button[value='in_transit']")
    in_transit_filter.click()
    expect(in_transit_filter).to_have_attribute("data-state", "checked")    

def test_delivered_filter_on_loads_page(logged_in: Page):
    """Check if the 'Delivered' filter on the loads page can be toggled"""
    page = logged_in        
    page.get_by_text("Sign In").click()
    page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
    page.get_by_role("menuitem", name="My Loads").click()
    expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
    delivered_filter = page.locator("button[value='delivered']")
    delivered_filter.click()
    expect(delivered_filter).to_have_attribute("data-state", "checked")

