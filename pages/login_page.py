class LoginPage:
    def __init__(self, page):
        self.page = page
    

    def open(self):
        self.page.goto("https://landing-dev.flexobo.com")
        self.page.get_by_text("Sign in").click()

    def login(self, mail, password):
        self.page.get_by_placeholder("Email or phone number is required").fill(mail)
        self.page.get_by_placeholder("Enter your password").fill(password)
        self.page.get_by_role("button", name="Sign in").click()

    def 