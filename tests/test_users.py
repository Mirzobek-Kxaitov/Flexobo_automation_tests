import time
import allure
import pytest
from playwright.sync_api import Page
from pages.users_page import UsersPage


# Users tab mavjud bo'lgan rollar
USERS_CAPABLE = ["broker", "carrier"]


@allure.feature("Company")
@allure.story("Invite user")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", USERS_CAPABLE)
def test_invite_user(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    email = f"invite_{int(time.time())}@test.com"

    UsersPage(page).invite_user(
        email=email,
    ).expect_invitation_visible(email)


@allure.feature("Company")
@allure.story("Resend invitation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("role", USERS_CAPABLE)
def test_resend_invitation(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    email = f"resend_{int(time.time())}@test.com"

    users = UsersPage(page)
    users.invite_user(email=email)
    users.resend_invitation(email).expect_resent_success()


@allure.feature("Company")
@allure.story("Cancel invitation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", USERS_CAPABLE)
def test_cancel_invitation(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    email = f"cancel_{int(time.time())}@test.com"

    users = UsersPage(page)
    users.invite_user(email=email)
    users.cancel_invitation(email).expect_no_pending()
