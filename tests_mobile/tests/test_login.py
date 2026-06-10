import os

import allure
import pytest

from tests_mobile.screens.loads_screen import LoadsScreen
from tests_mobile.screens.login_screen import LoginScreen
from tests_mobile.screens.home_screen import HomeScreen
from tests_mobile.screens.profile_screen import ProfileScreen
from tests_mobile.screens.access_restricted_screen import AccessRestrictedScreen
from tests_mobile.screens.forgot_password_screen import ForgotPasswordScreen
from tests_mobile.screens.register_screen import RegisterScreen


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Login")
@allure.story("Broker can log in and see loads screen")
def test_mobile_broker_login_success(fresh_mobile_app):
    email = os.getenv("BROKER_EMAIL")
    password = os.getenv("BROKER_PASSWORD")
    assert email and password, "BROKER_EMAIL/BROKER_PASSWORD must be set in .env"

    LoginScreen(fresh_mobile_app).login(email, password)
    LoadsScreen(fresh_mobile_app).expect_visible()


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Loads")
@allure.story("Loads screen shows main filter controls after login")
def test_mobile_loads_filter_controls_visible(fresh_mobile_app):
    email = os.getenv("BROKER_EMAIL")
    password = os.getenv("BROKER_PASSWORD")
    assert email and password, "BROKER_EMAIL/BROKER_PASSWORD must be set in .env"

    LoginScreen(fresh_mobile_app).login(email, password)
    LoadsScreen(fresh_mobile_app).expect_filter_controls_visible()


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Profile")
@allure.story("Broker can log out")
def test_mobile_broker_can_logout(fresh_mobile_app):
    email = os.getenv("BROKER_EMAIL")
    password = os.getenv("BROKER_PASSWORD")
    assert email and password, "BROKER_EMAIL/BROKER_PASSWORD must be set in .env"

    LoginScreen(fresh_mobile_app).login(email, password)
    LoadsScreen(fresh_mobile_app).expect_visible()

    ProfileScreen(fresh_mobile_app).open_from_bottom_nav().logout()
    LoginScreen(fresh_mobile_app).expect_visible()


@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.parametrize(
    "role,email_key,password_key",
    [
        ("broker", "BROKER_EMAIL", "BROKER_PASSWORD"),
        ("load_owner", "LOAD_OWNER_EMAIL", "LOAD_OWNER_PASSWORD"),
        ("carrier", "CARRIER_EMAIL", "CARRIER_PASSWORD"),
    ],
)
@allure.feature("Mobile Login")
@allure.story("Supported roles can log in")
def test_mobile_supported_roles_can_login(fresh_mobile_app, role, email_key, password_key):
    email = os.getenv(email_key)
    password = os.getenv(password_key)
    assert email and password, f"{email_key}/{password_key} must be set in .env"

    with allure.step(f"Log in as {role}"):
        LoginScreen(fresh_mobile_app).login(email, password)

    with allure.step("Verify app home screen is visible"):
        HomeScreen(fresh_mobile_app).expect_logged_in()


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Login")
@allure.story("Owner operator sees access restricted screen")
def test_mobile_owner_operator_access_is_restricted(fresh_mobile_app):
    email = os.getenv("OWNER_OPERATOR_EMAIL")
    password = os.getenv("OWNER_OPERATOR_PASSWORD")
    assert email and password, "OWNER_OPERATOR_EMAIL/OWNER_OPERATOR_PASSWORD must be set in .env"

    LoginScreen(fresh_mobile_app).login(email, password)
    AccessRestrictedScreen(fresh_mobile_app).expect_visible()


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Login")
@allure.story("Invalid credentials keep user on login screen")
def test_mobile_invalid_login_stays_on_login_screen(fresh_mobile_app):
    LoginScreen(fresh_mobile_app).login("wrong@example.com", "wrongpass123")
    LoginScreen(fresh_mobile_app).expect_visible()


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Login")
@allure.story("Forgot password opens recovery screen")
def test_mobile_forgot_password_opens_recovery_screen(fresh_mobile_app):
    LoginScreen(fresh_mobile_app).open_forgot_password()
    ForgotPasswordScreen(fresh_mobile_app).expect_visible()


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Login")
@allure.story("Forgot password keeps invalid email on recovery screen")
def test_mobile_forgot_password_invalid_email_stays_on_recovery_screen(fresh_mobile_app):
    LoginScreen(fresh_mobile_app).open_forgot_password()
    ForgotPasswordScreen(fresh_mobile_app).submit_email_or_phone("invalid-email")
    ForgotPasswordScreen(fresh_mobile_app).expect_visible()


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Registration")
@allure.story("Register link opens registration screen")
def test_mobile_register_opens_registration_screen(fresh_mobile_app):
    LoginScreen(fresh_mobile_app).open_register()
    RegisterScreen(fresh_mobile_app).expect_visible()
