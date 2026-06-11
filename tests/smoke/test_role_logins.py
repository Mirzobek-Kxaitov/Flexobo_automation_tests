import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

# Login muvaffaqiyatli bo'lsa, sayt user'ni /sign-in dan boshqa joyga olib chiqadi
# (odatda /loads, lekin ba'zan /profile/root — ikkalasi ham OK).
NOT_SIGN_IN = re.compile(r".*sign-in.*")


@allure.feature("Role login smoke")
@allure.story("Broker login")
def test_broker_can_login(logged_in_broker: Page):
    expect(logged_in_broker).not_to_have_url(NOT_SIGN_IN)


@allure.feature("Role login smoke")
@allure.story("Load owner login")
def test_load_owner_can_login(logged_in_load_owner: Page):
    expect(logged_in_load_owner).not_to_have_url(NOT_SIGN_IN)


@allure.feature("Role login smoke")
@allure.story("Carrier login")
def test_carrier_can_login(logged_in_carrier: Page):
    expect(logged_in_carrier).not_to_have_url(NOT_SIGN_IN)


@allure.feature("Role login smoke")
@allure.story("Owner operator login")
def test_owner_operator_can_login(logged_in_owner_operator: Page):
    expect(logged_in_owner_operator).not_to_have_url(NOT_SIGN_IN)
