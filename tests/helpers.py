"""Shared helper functions for limit enforcement tests."""
import os
import re

import pytest
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


def dismiss_cookie_banner(page: Page) -> None:
    """Dismiss cookie consent banner if visible."""
    btn = page.get_by_role("button", name="Accept")
    if btn.is_visible(timeout=1000):
        btn.click(force=True)
        page.wait_for_timeout(500)


def pick_future_date(page: Page) -> None:
    """Select first available date from next month in calendar widget."""
    page.get_by_role("button", name="Next month").click()
    page.wait_for_timeout(300)
    page.locator(
        "td[role='gridcell']:not([data-outside='true']) button:not([disabled])"
    ).first.click()
    page.wait_for_timeout(300)


def read_usage_counter(page: Page, label: str, limit: int) -> int:
    """Read a usage counter value from the Usage tab in profile.

    Args:
        page: Playwright page object (logged-in user).
        label: Counter card label, e.g. "Bids placed", "Fleet size".
        limit: Expected plan limit shown on the card (e.g. 3).

    Returns:
        Current counter value as int.
    """
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    card = (
        page.locator("div")
        .filter(has_text=label)
        .filter(has_text=f"/ {limit}")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(rf"(\d+)\s*/\s*{limit}", text)
    assert match, f"'{label}' counter not found in card text:\n{text}"
    return int(match.group(1))


def navigate_to_loads(page: Page) -> None:
    """Navigate to /loads page via nav link or direct goto."""
    load_nav = page.get_by_role("link", name=re.compile(r"^Load$|^Груз$"))
    if not load_nav.is_visible():
        page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.body.innerText.trim().length > 50",
            timeout=15000,
        )
    else:
        load_nav.click()
        page.wait_for_function(
            "() => document.body.innerText.trim().length > 50",
            timeout=15000,
        )


def navigate_to_transport(page: Page) -> None:
    """Navigate to /transport page with blank-page fallback."""
    transport_nav = page.get_by_role(
        "link", name=re.compile(r"^Transport$|^Транспорт$")
    )
    if transport_nav.is_visible():
        transport_nav.click()
    else:
        page.goto(f"{APP_URL}/transport", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    if page.locator("body").inner_text(timeout=3000).strip() == "":
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(5000)


def create_load(load_owner: Page, price: int) -> None:
    """Create a load as load_owner with the given price.

    Fills route (Tashkent -> Denain), load type, weight,
    transport type, and publishes.
    """
    load_owner.get_by_role("button", name="Add").click()
    load_owner.get_by_role("menuitem", name="Load").click()
    load_owner.wait_for_timeout(1000)

    load_owner.get_by_role("textbox", name="From").fill("TASH")
    load_owner.get_by_text("Tashkent", exact=True).click()
    load_owner.get_by_role("textbox", name="To").fill("DENA")
    load_owner.get_by_text("Denain", exact=True).click()

    load_owner.get_by_text("Load type", exact=True).click()
    load_owner.get_by_role("option", name="dovcha").click()

    load_owner.get_by_role("button", name="Date").click()
    pick_future_date(load_owner)

    dismiss_cookie_banner(load_owner)

    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    load_owner.get_by_role("textbox", name="Load weight").fill("12")
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    load_owner.get_by_role("combobox").filter(has_text="Transport type").click()
    load_owner.get_by_role("option", name="Mega truck").click()
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    load_owner.get_by_role("textbox", name="Price").fill(str(price))
    load_owner.get_by_role("button", name="Next").click()
    load_owner.wait_for_timeout(500)

    load_owner.get_by_role("button", name="Publish").click()
    load_owner.wait_for_timeout(3000)


def place_bid_on_load(bidder: Page, price: int) -> None:
    """Find a load by price on /loads and place a bid.

    Args:
        bidder: Playwright page for the bidding user (carrier / OO).
        price: The unique price used to identify the load card.
    """
    navigate_to_loads(bidder)

    thousands = price // 1000
    remainder = price % 1000
    price_pattern = re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}")
    load_card = bidder.get_by_text(price_pattern).first
    expect(load_card).to_be_visible(timeout=20000)
    load_card.click()
    bidder.wait_for_timeout(1500)

    bidder.get_by_role("button", name="Place a bid").first.click()
    bidder.wait_for_timeout(2000)

    dismiss_cookie_banner(bidder)

    bidder.get_by_role("button", name="Date").click()
    pick_future_date(bidder)

    bidder.get_by_role("button", name="Place a bid").last.click()
    bidder.wait_for_timeout(3000)

    # Detect bid limit modal
    limit_modal = bidder.get_by_text("Limit reached")
    if limit_modal.is_visible(timeout=3000):
        bidder.get_by_role("button", name="Maybe later").click()
        pytest.skip("Carrier daily bid limit reached — reset the account or run tomorrow")

    bidder.wait_for_timeout(2000)


def create_load_and_place_bid(
    load_owner: Page, bidder: Page, price: str
) -> None:
    """Full flow: load_owner creates a load, bidder places a bid on it."""
    price_int = int(price)
    create_load(load_owner, price_int)
    place_bid_on_load(bidder, price_int)


def add_trailer(page: Page, index: int, prefix: str = "TRL") -> None:
    """Add a trailer in Fleet > Trailers tab.

    Args:
        page: Logged-in page with fleet access.
        index: Unique index for gov number.
        prefix: Gov number prefix (default "TRL").
    """
    page.goto(f"{APP_URL}/tms/fleet")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    page.get_by_role("tab", name="Trailers").click()
    page.wait_for_timeout(1000)

    page.get_by_role("button", name="Add Trailer").click()
    page.wait_for_timeout(2000)

    page.get_by_text("Select country").click()
    page.get_by_role("option", name="United Arab Emirates").click()
    page.wait_for_timeout(500)

    page.get_by_role("textbox", name="Gov. Number*").click()
    page.get_by_role("textbox", name="Gov. Number*").fill(f"{prefix}-{index:03d}")
    page.wait_for_timeout(500)

    page.get_by_role("combobox").filter(has_text="Trailer Type").click()
    page.get_by_role("option", name="Trailer 1").click()
    page.wait_for_timeout(500)

    page.get_by_role("combobox").filter(has_text=re.compile(r"^$")).click()
    page.get_by_role("option", name="2018").click()
    page.wait_for_timeout(500)

    page.get_by_role("button", name="Add").click()
    page.wait_for_timeout(3000)


def create_role(page: Page, name: str) -> None:
    """Create a company role in Profile > Roles tab."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    page.get_by_role("tab", name="Roles").click()
    page.wait_for_timeout(1500)

    page.get_by_role("button", name="Create role").click()
    page.wait_for_timeout(1500)

    page.get_by_role("textbox", name="Role name").click()
    page.get_by_role("textbox", name="Role name").fill(name)
    page.wait_for_timeout(500)

    page.get_by_role("button", name="Create role").click()
    page.wait_for_timeout(3000)


def invite_employee(page: Page, index: int, prefix: str = "emp") -> None:
    """Invite an employee in Profile > Users tab."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    page.get_by_role("tab", name="Users").click()
    page.wait_for_timeout(1500)

    page.get_by_role("button", name="Invite User").click()
    page.wait_for_timeout(1500)

    page.get_by_role("textbox", name="Phone or Email").fill(
        f"{prefix}_{index}@test.com"
    )
    page.wait_for_timeout(500)

    page.get_by_role("combobox", name="Role").click()
    page.get_by_role("option").first.click()
    page.wait_for_timeout(500)

    page.get_by_role("button", name="Send Invitation").click()
    page.wait_for_timeout(3000)
