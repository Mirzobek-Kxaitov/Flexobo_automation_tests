import os
import allure
import pytest
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


# Sidebar item visibility matrix
# True  = item ko'rinishi kerak
# False = item yashirin bo'lishi kerak
SIDEBAR_VISIBILITY = {
    "Profile":        {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": True},
    "Usage":          {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": True},
    "My bids":        {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": True},
    "Received bids":  {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": True},
    "My boards":      {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": False},
    "Invited boards": {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": True},
    "My trips":       {"broker": True,  "load_owner": False, "carrier": True,  "owner_operator": True},
    "My loads":       {"broker": True,  "load_owner": True,  "carrier": False, "owner_operator": False},
    "Users":          {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": False},
    "Roles":          {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": False},
    "My Invitations": {"broker": True,  "load_owner": False, "carrier": False, "owner_operator": True},
    "My Offers":      {"broker": False, "load_owner": False, "carrier": False, "owner_operator": True},
    "Fleet":          {"broker": True,  "load_owner": False, "carrier": True,  "owner_operator": True},
    "Drivers":        {"broker": True,  "load_owner": False, "carrier": True,  "owner_operator": False},
    "Orders":         {"broker": True,  "load_owner": True,  "carrier": True,  "owner_operator": True},
}


@allure.feature("Permissions")
@allure.story("Sidebar visibility per role")
@pytest.mark.parametrize("role", ["broker", "load_owner", "carrier", "owner_operator"])
def test_sidebar_visibility(request, role: str):
    """
    Profile sahifasidagi sidebar item'larini role bo'yicha tekshiradi.
    Bitta testda 15 ta item — barcha xatolar yig'ilib bir martada chiqariladi.
    """
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)  # React rendering — networkidle ishlamaydi (uzluksiz polling)

    failures = []

    for item, role_perms in SIDEBAR_VISIBILITY.items():
        expected_visible = role_perms[role]
        locator = page.get_by_text(item, exact=True).first
        actual_visible = locator.is_visible()

        if actual_visible != expected_visible:
            failures.append(
                f"  '{item}': expected={'visible' if expected_visible else 'hidden'}, "
                f"actual={'visible' if actual_visible else 'hidden'}"
            )

    if failures:
        pytest.fail(
            f"Sidebar visibility errors for {role}:\n" + "\n".join(failures)
        )
