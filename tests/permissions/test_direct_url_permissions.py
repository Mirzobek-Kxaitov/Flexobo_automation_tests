import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

# Ruhsat berilmagan URL'ga goto qilingan user shu sahifaga yuboriladi
FORBIDDEN_REDIRECT_URL = f"{APP_URL}/profile/root"


# URL × role permission matrix
# True: URL ochiladi va sahifada qoladi
# False: /profile/root ga redirect bo'ladi
DIRECT_URL_PERMISSIONS = {
    "/loads/create": {
        "broker": True,
        "load_owner": True,
        "carrier": False,
        "owner_operator": False,
    },
    "/trips/create": {
        "broker": True,
        "load_owner": False,
        "carrier": True,
        "owner_operator": True,
    },
    "/tms/fleet": {
        "broker": True,
        "load_owner": False,
        "carrier": True,
        "owner_operator": True,
    },
    "/tms/drivers": {
        "broker": True,
        "load_owner": False,
        "carrier": True,
        "owner_operator": False,
    },
    "/tms/orders": {
        "broker": True,
        "load_owner": True,
        "carrier": True,
        "owner_operator": True,
    },
}


@allure.feature("Permissions")
@allure.story("Direct URL access")
@pytest.mark.parametrize("role", ["broker", "load_owner", "carrier", "owner_operator"])
@pytest.mark.parametrize("path", ["/loads/create", "/trips/create", "/tms/fleet", "/tms/drivers", "/tms/orders"])
def test_direct_url_permission(request, role: str, path: str):
    """
    Direct URL'ga to'g'ridan-to'g'ri o'tib ko'rish:
    - Ruxsat berilgan role: URL o'zgarmasdan qoladi
    - Ruxsat berilmagan role: aniq /profile/root ga redirect bo'lishi kerak
    """
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    can_access = DIRECT_URL_PERMISSIONS[path][role]
    target_url = f"{APP_URL}{path}"

    page.goto(target_url)

    if can_access:
        expect(page).to_have_url(target_url)
    else:
        expect(page).to_have_url(FORBIDDEN_REDIRECT_URL)
