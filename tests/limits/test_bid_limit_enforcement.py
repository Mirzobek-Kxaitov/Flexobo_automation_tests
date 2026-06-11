"""
Bid limit enforcement tests — verifies that Free plan limit is enforced in practice.

Scenario:
1. Bring the broker to the 20/20 bid limit (load_owner creates loads, broker bids)
2. Attempt to place bid #21 -> "Limit reached" modal appears
3. Modal behavior: "Maybe later" (closes modal), "Upgrade plan" (navigates to upgrade page)

Pre-condition: load_owner must be able to create enough loads.
"""
import os
import re
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.loads_page import LoadsPage
from tests.helpers import read_usage_counter

load_dotenv()
APP_URL = os.getenv("APP_URL")

BID_LIMIT = 20


def _create_load_and_get_price(load_owner_page: Page, index: int) -> str:
    """Create a load as load_owner and return its unique price string."""
    price = str(10000 + index)  # 10001, 10002, ... — each is unique
    LoadsPage(load_owner_page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        body_type="Mega truck",
        price=price,
    )
    load_owner_page.wait_for_timeout(3000)
    return price


def _place_bid_on_load(broker_page: Page, price: str, note: str) -> None:
    """Find the load by price on the broker's loads page and place a bid."""
    price_pattern = re.compile(rf"USD\s*{int(price):,}")

    broker_page.goto(f"{APP_URL}/loads")
    broker_page.wait_for_load_state("domcontentloaded")
    broker_page.wait_for_timeout(3500)

    broker_page.get_by_text(price_pattern).first.click()
    broker_page.wait_for_timeout(2500)

    broker_page.get_by_role("button", name="Place a bid").first.click()
    broker_page.wait_for_timeout(2500)

    broker_page.get_by_placeholder("Why is your offer better than others?").fill(note)
    broker_page.wait_for_timeout(500)

    broker_page.get_by_role("button", name="Place a bid").last.click()
    broker_page.wait_for_timeout(5000)


@allure.feature("Plan Limits")
@allure.story("Free plan: fill to limit and verify 'Limit reached' modal")
@allure.severity(allure.severity_level.CRITICAL)
def test_bid_limit_full_flow(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    Bring broker to 20/20 bids and verify that bid #21 triggers
    the 'Limit reached' modal.

    Steps:
    1. Read current bid count from Usage page
    2. Fill up to the limit by creating loads and placing bids
    3. Confirm counter reached the limit
    4. Place one more bid and verify the modal appears
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Read current bids placed from Usage page"):
        current = read_usage_counter(broker, "Bids placed", BID_LIMIT)
        needed = BID_LIMIT - current

    with allure.step(f"Fill up to limit: {current}/{BID_LIMIT}, need {needed} more bids"):
        for i in range(needed):
            bid_num = current + i + 1
            with allure.step(f"Place bid #{bid_num}/{BID_LIMIT}"):
                price = _create_load_and_get_price(owner, bid_num)
                _place_bid_on_load(broker, price, f"Fill bid #{bid_num}")

    with allure.step("Confirm counter reached the limit"):
        final = read_usage_counter(broker, "Bids placed", BID_LIMIT)
        assert final == BID_LIMIT, (
            f"Expected {BID_LIMIT}/{BID_LIMIT}, got {final}/{BID_LIMIT}"
        )

    with allure.step("Place one over-limit bid and expect 'Limit reached' modal"):
        extra_price = _create_load_and_get_price(owner, BID_LIMIT + 1)
        _place_bid_on_load(broker, extra_price, "Over limit bid")

    with allure.step("Verify 'Limit reached' modal is visible with expected buttons"):
        expect(
            broker.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

        expect(
            broker.get_by_text("You have reached your limit")
        ).to_be_visible()

        expect(
            broker.get_by_role("button", name="Upgrade plan")
        ).to_be_visible()

        expect(
            broker.get_by_role("button", name="Maybe later")
        ).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("'Limit reached' modal: 'Maybe later' dismisses modal")
@allure.severity(allure.severity_level.NORMAL)
def test_limit_modal_maybe_later(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    When the broker is at the bid limit and places another bid,
    clicking 'Maybe later' on the modal should close it.

    Pre-condition: broker must already be at 20/20.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Check that broker is already at the bid limit"):
        current = read_usage_counter(broker, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{BID_LIMIT}. "
                f"Run test_bid_limit_full_flow first."
            )

    with allure.step("Create a new load and attempt to place an over-limit bid"):
        price = _create_load_and_get_price(owner, 9001)
        _place_bid_on_load(broker, price, "Maybe later test")

    with allure.step("Verify 'Limit reached' modal appears"):
        expect(
            broker.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Maybe later' and verify modal closes"):
        broker.get_by_role("button", name="Maybe later").click()
        broker.wait_for_timeout(1000)

        expect(
            broker.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("'Limit reached' modal: 'Upgrade plan' navigates to upgrade page")
@allure.severity(allure.severity_level.NORMAL)
def test_limit_modal_upgrade_plan(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """
    When the broker is at the bid limit and places another bid,
    clicking 'Upgrade plan' should navigate to the pricing/upgrade page.

    Pre-condition: broker must already be at 20/20.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Check that broker is already at the bid limit"):
        current = read_usage_counter(broker, "Bids placed", BID_LIMIT)
        if current < BID_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{BID_LIMIT}. "
                f"Run test_bid_limit_full_flow first."
            )

    with allure.step("Create a new load and attempt to place an over-limit bid"):
        price = _create_load_and_get_price(owner, 9002)
        _place_bid_on_load(broker, price, "Upgrade plan test")

    with allure.step("Verify 'Limit reached' modal appears"):
        expect(
            broker.get_by_role("heading", name="Limit reached")
        ).to_be_visible(timeout=10000)

    with allure.step("Click 'Upgrade plan' and verify navigation to pricing page"):
        broker.get_by_role("button", name="Upgrade plan").click()
        broker.wait_for_timeout(3000)

        expect(broker).to_have_url(re.compile(r".*(pricing|upgrade|plan).*"), timeout=10000)
