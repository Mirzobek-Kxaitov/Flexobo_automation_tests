import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


# Login talab qiluvchi himoyalangan URL'lar
# Login'siz kira olmasligi va /sign-in ga redirect bo'lishi kerak
PROTECTED_URLS = [
    "/loads/create",
    "/trips/create",
    "/tms/fleet",
    "/tms/drivers",
    "/tms/orders",
    "/profile/root",
]


@allure.feature("Permissions")
@allure.story("Unauthenticated redirect")
@pytest.mark.parametrize("path", PROTECTED_URLS)
def test_unauthenticated_redirected_to_signin(page: Page, path: str):
    """
    Login qilmagan user himoyalangan URL'ga goto qilsa,
    /sign-in sahifasiga avtomatik redirect bo'lishi kerak.
    """
    page.goto(f"{APP_URL}{path}")
    expect(page).to_have_url(re.compile(r".*sign-in.*"))
