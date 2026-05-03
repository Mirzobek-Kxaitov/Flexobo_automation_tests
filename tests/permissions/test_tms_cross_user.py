"""
TMS sahifalarida cross-user isolation testlari.

⚠️  Bu testlar MOCK environment'da SKIP qilinadi:
Mock env'da TMS seed data hamma user'larga bir xil ulanadi
(carrier va broker bir xil HYUNDAI truck, Mirzobek Xaitov driver,
#ORD-... order ko'radi). Demak privacy isolation'ni test qilish
imkoni yo'q.

Real backend (staging / prod) environment'da bu testlar bekor
qilinishi va passed bo'lishi kutiladi.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

SKIP_MOCK_ENV = pytest.mark.skip(
    reason="Mock env shares TMS seed data across users — privacy isolation only "
           "verifiable on a real backend with distinct company data."
)


@SKIP_MOCK_ENV
@allure.feature("Permissions")
@allure.story("TMS cross-user: fleet isolation")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_does_not_see_brokers_trucks_in_fleet(logged_in_broker: Page,
                                                     logged_in_carrier: Page):
    """Broker'ning truck'i (ABC123321) carrier fleet'ida ko'rinmasligi kerak."""
    logged_in_broker.goto(f"{APP_URL}/tms/fleet")
    logged_in_broker.wait_for_timeout(3000)
    assert "HYUNDAI" in logged_in_broker.locator("body").inner_text()

    logged_in_carrier.goto(f"{APP_URL}/tms/fleet")
    logged_in_carrier.wait_for_timeout(3000)
    expect(
        logged_in_carrier.get_by_text("ABC123321").first
    ).not_to_be_visible(timeout=5000)


@SKIP_MOCK_ENV
@allure.feature("Permissions")
@allure.story("TMS cross-user: drivers isolation")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_does_not_see_brokers_drivers_in_list(logged_in_broker: Page,
                                                     logged_in_carrier: Page):
    """Broker'ning driver email'i carrier drivers'ida ko'rinmasligi kerak."""
    logged_in_broker.goto(f"{APP_URL}/tms/drivers")
    logged_in_broker.wait_for_timeout(3000)
    assert "Mirzobek Xaitov" in logged_in_broker.locator("body").inner_text()

    logged_in_carrier.goto(f"{APP_URL}/tms/drivers")
    logged_in_carrier.wait_for_timeout(3000)
    expect(
        logged_in_carrier.get_by_text("pistonchijon@mail.ru").first
    ).not_to_be_visible(timeout=5000)


@SKIP_MOCK_ENV
@allure.feature("Permissions")
@allure.story("TMS cross-user: orders isolation")
@allure.severity(allure.severity_level.CRITICAL)
def test_carrier_does_not_see_brokers_orders(logged_in_broker: Page,
                                             logged_in_carrier: Page):
    """Broker'ning order'i (#ORD-...) carrier orders'ida ko'rinmasligi kerak."""
    logged_in_broker.goto(f"{APP_URL}/tms/orders")
    logged_in_broker.wait_for_timeout(3000)
    match = re.search(r"#ORD-[\w-]+", logged_in_broker.locator("body").inner_text())
    assert match
    broker_order_id = match.group(0)

    logged_in_carrier.goto(f"{APP_URL}/tms/orders")
    logged_in_carrier.wait_for_timeout(3000)
    expect(
        logged_in_carrier.get_by_text(broker_order_id).first
    ).not_to_be_visible(timeout=5000)
