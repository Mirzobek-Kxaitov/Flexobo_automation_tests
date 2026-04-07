from playwright.sync_api import Page, expect

#Helper functions
def open_login_page(page: Page):
    page.goto("https://landing-dev.flexobo.com/")
    page.get_by_text("Sign In").click()

def login(page: Page, email: str, password: str):
    page.get_by_placeholder("Email or phone number is required").fill(email)
    page.get_by_placeholder("Enter your password").fill(password)
    page.get_by_role("button", name="Sign In").click()


# def test_valid_login(page: Page):
#     #Arrange
#     open_login_page(page)
#     #Act
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")

# def test_invalid_login(page: Page):
#     #Arrange
#     open_login_page(page)
#     #Act
#     login(page, "Palnchixon@mail.ru", "123321")
#     #Assert
#     expect(page.get_by_text("Invalid phone number or email")).to_be_visible()

# def test_empty_email_login(page: Page):
#     #Arrange
#     open_login_page(page)
#     #Act
#     login(page, "", "123321")
#     #Assert
#     expect(page.get_by_text("Email or phone number is required")).to_be_visible()

# def test_empty_password_login(page: Page):
#     #Arrange
#     open_login_page(page)
#     #Act
#     login(page, "Palonchixon@mail.ru", "")
#     #Assert
#     expect(page.get_by_text("Password is required")).to_be_visible()

# def test_user_can_logout(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="Logout").click()
#     # #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")





# def test_open_profile_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="Profile").click()
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/profile/root")




# def test_my_loads_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="My Loads").click()
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")

# def test_my_trucks_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="Fleet").click()
#     expect(page).to_have_url("https://app.flexobo-mock.site/tms/fleet")


# def test_my_trips_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click() 
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="My trips").click()
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/profile-trips")
    
#----------------------------------------------------------------------------------------
# def test_user_can_login(page: Page):
#     #Arrange
#     open_login_page(page)

#     #Act
#     page.get_by_placeholder("Email or phone number is required").fill("majab76105@exespay.com")
#     page.get_by_placeholder("Enter your password").fill("123321")
#     page.get_by_role("button", name="Sign In").click()
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     page.get_by_text("Sign In").click()
    
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/loads")
 

# # def test_user_cannot_login_with_invalid_credentials(page: Page):
# #     page.goto("https://landing-dev.flexobo.com/")
# #     #Arrange

# #     #Act
# #     page.get_by_text("Sign In").click()
# #     expect(page).to_have_url("https://app.flexobo-mock.site/sign-in?from_landing=true")
    
# #     page.get_by_placeholder("Email or phone number is required").fill("Palonchibek@mail.ru")
# #     page.get_by_placeholder("Enter your password").fill("123321")
# #     page.get_by_role("button", name="Sign In").click()

# #     #Assert
# #     expect(page.get_by_text("Invalid phone number or email")).to_be_visible()
    


# # def test_user_cannot_login_with_empty_email(page: Page):
# #     #Arrange
# #     page.goto("https://landing-dev.flexobo.com/")

# #     #Act
# #     page.get_by_text("Sign In").click()
# #     expect(page).to_have_url("https://app.flexobo-mock.site/sign-in?from_landing=true")
# #     page.get_by_placeholder("Enter your password").fill("123321")
# #     page.get_by_role("button", name="Sign In").click()

# #     #Assert
# #     expect(page.get_by_text("Email or phone number is required")).to_be_visible()

# def test_user_cannot_login_with_empty_password(page: Page):
#     #Arrange
#     open_login_page(page)

#     #Act
#     page.get_by_placeholder("Email or phone number is required").fill("majab76105@exespay.com")
#     page.get_by_role("button", name="Sign In").click()

#     #Assert
#     expect(page.get_by_text("Password is required")).to_be_visible()




# def test_filter_in_contract_on_loads_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="My Loads").click()
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
#     in_contract_filter = page.locator("button[value='in_contract']")
#     in_contract_filter.click()
#     expect(in_contract_filter).to_have_attribute("data-state", "checked")

# def test_filter_in_transit_on_loads_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="My Loads").click()
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
#     in_transit_filter = page.locator("button[value='in_transit']")
#     in_transit_filter.click()
#     expect(in_transit_filter).to_have_attribute("data-state", "checked")


# def test_filter_delivered_on_loads_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321")
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="My Loads").click()
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
#     delivered_filter = page.locator("button[value='delivered']")
#     delivered_filter.click()
#     expect(delivered_filter).to_have_attribute("data-state", "checked")

# def test_template_button_on_settings_page(page: Page):
#     #Arrange
#     open_login_page(page)
#     login(page, "majab76105@exespay.com", "123321") 
#     #Assert
#     expect(page).to_have_url("https://landing-dev.flexobo.com/")
#     #Act
#     page.get_by_text("Sign In").click()
#     page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).click()
#     page.get_by_role("menuitem", name="My Loads").click()
#     #Assert
#     expect(page).to_have_url("https://app.flexobo-mock.site/profile-load")
#     #Act
#     with page.expect_download() as download_info:
#         page.get_by_role("button", name="Template").click()

#     download = download_info.value
#     filename = download.suggested_filename

#     assert filename.endswith(".xlsx")