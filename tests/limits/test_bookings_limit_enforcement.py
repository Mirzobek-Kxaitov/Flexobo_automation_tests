"""
Bookings limit enforcement tests — Free plan restriction.

Scenario:
1. Broker creates 5 bookings (0 -> 5/5).
2. On the 6th booking attempt a 'Limit reached' modal appears.
3. Modal behaviour: 'Maybe later' closes it, 'Upgrade plan' navigates away.

Multi-user flow:
- load_owner: creates a load, accepts the broker's bid.
- broker: places a bid (booking is counted against the broker).

Backend note: on the booking.created event customerId = bidderId (broker),
so the broker's Bookings counter increments.

Free plan: Bookings limit = 5.
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

BOOKINGS_LIMIT = 5


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _create_booking(load_owner: Page, broker: Page, price: str) -> None:
    """Create one booking end-to-end.

    Steps:
    - load_owner creates a load with the given price.
    - broker finds the load and places a bid.
    - load_owner accepts the bid.
    This causes the broker's Bookings counter to increment by 1.
    """
    price_pattern = re.compile(rf"USD\s*{int(price):,}")

    with allure.step("Load owner creates a load"):
        LoadsPage(load_owner).create_load(
            from_city="Toshkent",
            from_suggestion="Tashkent, 100000, Uzbekistan",
            to_city="Termez",
            to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
            load_type="Apple production",
            weight="20",
            day="20",
            body_type="'/40' extendable semi-trailer",
            price=price,
            loading_type="Hydraulic",
            unloading_type="Pneumatic",
        )
        load_owner.wait_for_timeout(3000)

    with allure.step("Broker finds the load and places a bid"):
        broker.goto(f"{APP_URL}/loads")
        broker.wait_for_load_state("domcontentloaded")
        broker.wait_for_timeout(3500)

        broker.get_by_text(price_pattern).first.click()
        broker.wait_for_timeout(2500)

        broker.get_by_role("button", name="Place a bid").first.click()
        broker.wait_for_timeout(2500)

        broker.get_by_placeholder("Why is your offer better than others?").fill(
            f"Bookings limit test — {price}"
        )
        broker.wait_for_timeout(500)

        broker.get_by_role("button", name="Place a bid").last.click()
        broker.wait_for_timeout(5000)

    with allure.step("Load owner accepts the bid"):
        load_owner.goto(f"{APP_URL}/profile/root")
        load_owner.wait_for_timeout(3000)
        load_owner.get_by_text("Received bids", exact=True).first.click()
        load_owner.wait_for_timeout(5000)

        load_owner.get_by_text(price_pattern).first.click()
        load_owner.wait_for_timeout(2500)

        bid_button = (
            load_owner.get_by_role("button")
            .filter(has_text=price_pattern)
            .filter(has_text=re.compile(r"broker", re.IGNORECASE))
            .first
        )
        bid_button.click()
        load_owner.wait_for_timeout(2000)

        load_owner.get_by_role("button", name="Accept").click()
        load_owner.wait_for_timeout(5000)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Bookings limit enforcement is not working — backend bug: "
        "bookings continue to be created even after reaching 5/5"
    )
)
@allure.feature("Plan Limits")
@allure.story("Free plan: fill bookings to limit and verify 'Limit reached' modal")
@allure.severity(allure.severity_level.CRITICAL)
def test_bookings_limit_full_flow(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """Verify that a 'Limit reached' modal appears when the broker exceeds
    the free-plan bookings limit.

    Steps:
    1. Read the current bookings counter from the Usage tab.
    2. Fill up to the limit (each iteration: load -> bid -> accept).
    3. Confirm the counter reached the limit.
    4. Attempt one more booking and verify the modal is shown.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Read current bookings counter from Usage tab"):
        current = read_usage_counter(broker, "Bookings", BOOKINGS_LIMIT)
        needed = BOOKINGS_LIMIT - current

    with allure.step(f"Fill bookings up to limit (current={current}, needed={needed})"):
        for i in range(needed):
            booking_num = current + i + 1
            price = str(10000 + booking_num)
            with allure.step(f"Create booking #{booking_num}/{BOOKINGS_LIMIT} (price={price})"):
                _create_booking(owner, broker, price)

    with allure.step("Confirm bookings counter reached the limit"):
        final = read_usage_counter(broker, "Bookings", BOOKINGS_LIMIT)
        assert final >= BOOKINGS_LIMIT, (
            f"Expected >= {BOOKINGS_LIMIT}/{BOOKINGS_LIMIT}, got {final}/{BOOKINGS_LIMIT}"
        )

    with allure.step("Attempt one more booking beyond the limit"):
        _create_booking(owner, broker, str(10000 + BOOKINGS_LIMIT + 1))

    with allure.step("Verify 'Limit reached' modal is displayed on broker or owner page"):
        modal_page = None
        for p in [broker, owner]:
            try:
                p.get_by_role("heading", name="Limit reached").wait_for(
                    state="visible"
                )
                modal_page = p
                break
            except Exception:
                pass

        assert modal_page is not None, (
            "'Limit reached' modal was not found on any page"
        )
        expect(modal_page.get_by_text("You have reached your limit")).to_be_visible()
        expect(modal_page.get_by_role("button", name="Upgrade plan")).to_be_visible()
        expect(modal_page.get_by_role("button", name="Maybe later")).to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Bookings limit modal: 'Maybe later' dismisses modal")
@allure.severity(allure.severity_level.NORMAL)
def test_bookings_modal_maybe_later(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """Verify that clicking 'Maybe later' closes the bookings limit modal.

    Pre-condition: broker must already be at 5/5 bookings.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Check broker is already at the bookings limit"):
        current = read_usage_counter(broker, "Bookings", BOOKINGS_LIMIT)
        if current < BOOKINGS_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{BOOKINGS_LIMIT}. "
                f"Run test_bookings_limit_full_flow first."
            )

    with allure.step("Attempt a booking beyond the limit to trigger modal"):
        _create_booking(owner, broker, "19001")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            broker.get_by_role("heading", name="Limit reached")
        ).to_be_visible()

    with allure.step("Click 'Maybe later' and verify modal is dismissed"):
        broker.get_by_role("button", name="Maybe later").click()
        broker.wait_for_timeout(1000)
        expect(
            broker.get_by_role("heading", name="Limit reached")
        ).not_to_be_visible()


@allure.feature("Plan Limits")
@allure.story("Bookings limit modal: 'Upgrade plan' navigates to upgrade page")
@allure.severity(allure.severity_level.NORMAL)
def test_bookings_modal_upgrade_plan(
    logged_in_broker: Page, logged_in_load_owner: Page
):
    """Verify that clicking 'Upgrade plan' navigates to the pricing/upgrade page.

    Pre-condition: broker must already be at 5/5 bookings.
    """
    broker = logged_in_broker
    owner = logged_in_load_owner
    broker.set_default_timeout(60000)
    owner.set_default_timeout(60000)

    with allure.step("Check broker is already at the bookings limit"):
        current = read_usage_counter(broker, "Bookings", BOOKINGS_LIMIT)
        if current < BOOKINGS_LIMIT:
            pytest.skip(
                f"Broker is at {current}/{BOOKINGS_LIMIT}. "
                f"Run test_bookings_limit_full_flow first."
            )

    with allure.step("Attempt a booking beyond the limit to trigger modal"):
        _create_booking(owner, broker, "19002")

    with allure.step("Verify 'Limit reached' modal is visible"):
        expect(
            broker.get_by_role("heading", name="Limit reached")
        ).to_be_visible()

    with allure.step("Click 'Upgrade plan' and verify navigation to pricing page"):
        broker.get_by_role("button", name="Upgrade plan").click()
        broker.wait_for_timeout(3000)
        expect(broker).to_have_url(
            re.compile(r".*(pricing|upgrade|plan).*")
        )
