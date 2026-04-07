from playwright.sync_api import Page, expect
def test_valid_login(open_page: Page):
    open_page.get_by_placeholder("Email or phone number is required").fill("majab76105@exespay.com")
    open_page.get_by_placeholder("Enter your password").fill("123321")
    open_page.get_by_role("button", name="Sign In").click()
    expect(open_page).to_have_url("https://landing-dev.flexobo.com/")

def test_invalid_login(open_page: Page):
    """Enter the system with invalid credentials and check if the error message is displayed"""
    open_page.get_by_placeholder("Email or phone number is required").fill("wrong@example.com")
    open_page.get_by_placeholder("Enter your password").fill("123321")
    open_page.get_by_role("button", name="Sign In").click()
    expect(open_page.get_by_text("Invalid phone number or email")).to_be_visible()

def test_empty_email(open_page: Page):
    """Try to log in without entering an email and check if the appropriate error message is displayed"""
    open_page.get_by_placeholder("Enter your password").fill("123321")
    open_page.get_by_role("button", name="Sign In").click()
    expect(open_page.get_by_text("Email or phone number is required")).to_be_visible()

def test_empty_password(open_page: Page):
    """Try to log in without entering a password and check if the appropriate error message is displayed"""
    open_page.get_by_placeholder("Email or phone number is required").fill("majab76105@exespay.com")
    open_page.get_by_role("button", name="Sign In").click()
    expect(open_page.get_by_text("Password is required")).to_be_visible()   