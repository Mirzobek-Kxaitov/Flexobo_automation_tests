import os

import allure
import pytest

from tests_mobile.screens.load_detail_screen import LoadDetailScreen
from tests_mobile.screens.loads_screen import LoadsScreen
from tests_mobile.screens.login_screen import LoginScreen


@pytest.mark.mobile
@pytest.mark.smoke
@allure.feature("Mobile Place a Bid")
@allure.story("Loads board -> click load -> detail screen opens")
def test_mobile_clicking_load_opens_detail_screen(fresh_mobile_app):
    email = os.getenv("CARRIER_EMAIL")
    password = os.getenv("CARRIER_PASSWORD")
    assert email and password, "CARRIER_EMAIL/CARRIER_PASSWORD must be set in .env"

    LoginScreen(fresh_mobile_app).login(email, password)
    load_summary = LoadsScreen(fresh_mobile_app).open_first_load_card()

    LoadDetailScreen(fresh_mobile_app).expect_visible_for_load(load_summary)
