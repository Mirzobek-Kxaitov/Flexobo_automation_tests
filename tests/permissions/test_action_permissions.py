import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


# Profile sahifasidagi action tugmalarining role bo'yicha ko'rinishi
# True = ko'rinishi kerak, False = yashirin bo'lishi kerak
BUTTON_VISIBILITY = {
    "Update Password": {
        "broker": True, "load_owner": True, "carrier": True, "owner_operator": True,
    },
    "Verify Identity": {
        "broker": True, "load_owner": True, "carrier": True, "owner_operator": True,
    },
    "Enable 2FA": {
        "broker": True, "load_owner": True, "carrier": True, "owner_operator": True,
    },
}


@allure.feature("Permissions")
@allure.story("Profile action buttons visibility")
@pytest.mark.parametrize("role", ["broker", "load_owner", "carrier", "owner_operator"])
@pytest.mark.parametrize("button_name", list(BUTTON_VISIBILITY.keys()))
def test_profile_action_button_visibility(request, role: str, button_name: str):
    """
    Profile sahifasidagi har action tugmasining role bo'yicha to'g'ri ko'rinishi.
    """
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    button = page.get_by_role("button", name=button_name).first
    expected_visible = BUTTON_VISIBILITY[button_name][role]

    if expected_visible:
        expect(button).to_be_visible()
    else:
        expect(button).not_to_be_visible()
