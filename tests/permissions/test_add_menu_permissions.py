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
    item_test_ids = {
        "Load": "global_add_load_menu_item",
        "Transport": "global_add_transport_menu_item",
    }

    add_btn = page.get_by_test_id("global_add_button")
    expect(add_btn).to_be_visible()
    add_btn.click()
    item = page.get_by_test_id(item_test_ids[menu_item])

    if should_be_visible:
        expect(item).to_be_visible()
    else:
        expect(item).not_to_be_visible()
