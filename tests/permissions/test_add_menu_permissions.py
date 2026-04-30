import allure
import pytest
from playwright.sync_api import Page, expect


# Permission matrix: kim qaysi "Add" menyu itemini ko'ra olishi
# Yangi item qo'shilsa — shu yerga qator qo'shiladi
ADD_MENU_PERMISSIONS = {
    "Load": {
        "broker": True,
        "load_owner": True,
        "carrier": False,
        "owner_operator": False,
    },
    "Transport": {
        "broker": True,
        "load_owner": False,
        "carrier": True,
        "owner_operator": True,
    },
}


@allure.feature("Permissions")
@allure.story("Add menu — role-based visibility")
@pytest.mark.parametrize("role", ["broker", "load_owner", "carrier", "owner_operator"])
@pytest.mark.parametrize("menu_item", ["Load", "Transport"])
def test_add_menu_item_visibility(request, role: str, menu_item: str):
    """Add menyudagi har item'ning role bo'yicha ko'rinishini tekshiradi."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    should_be_visible = ADD_MENU_PERMISSIONS[menu_item][role]

    page.get_by_role("button", name="Add").click()
    item = page.get_by_role("menuitem", name=menu_item)

    if should_be_visible:
        expect(item).to_be_visible()
    else:
        expect(item).not_to_be_visible()
