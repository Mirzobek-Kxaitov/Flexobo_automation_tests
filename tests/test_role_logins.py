import os
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


@allure.feature("Role login smoke")
@allure.story("Broker login")
def test_broker_can_login(logged_in_broker: Page):
    expect(logged_in_broker).to_have_url(f"{APP_URL}/loads")


@allure.feature("Role login smoke")
@allure.story("Load owner login")
def test_load_owner_can_login(logged_in_load_owner: Page):
    expect(logged_in_load_owner).to_have_url(f"{APP_URL}/loads")


@allure.feature("Role login smoke")
@allure.story("Carrier login")
def test_carrier_can_login(logged_in_carrier: Page):
    expect(logged_in_carrier).to_have_url(f"{APP_URL}/loads")


@allure.feature("Role login smoke")
@allure.story("Owner operator login")
def test_owner_operator_can_login(logged_in_owner_operator: Page):
    expect(logged_in_owner_operator).to_have_url(f"{APP_URL}/loads")
