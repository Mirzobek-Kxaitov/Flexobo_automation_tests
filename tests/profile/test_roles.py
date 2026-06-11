import time
import allure
import pytest
from playwright.sync_api import Page
from pages.roles_page import RolesPage


# Roles tab mavjud bo'lgan rollar
ROLES_CAPABLE = ["broker", "carrier"]


@allure.feature("Company")
@allure.story("Create role")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", ROLES_CAPABLE)
def test_create_role(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    name = f"role-{int(time.time())}"
    RolesPage(page).create_role(name).expect_role_visible(name)


@allure.feature("Company")
@allure.story("Delete role")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", ROLES_CAPABLE)
def test_delete_role(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    name = f"del-role-{int(time.time())}"
    roles = RolesPage(page)
    roles.create_role(name).expect_role_visible(name)
    roles.delete_role(name).expect_on_roles_tab()
