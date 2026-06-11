"""Shared helper functions for limit enforcement tests."""
import os
import re

import pytest
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

def price_regex(price: int) -> re.Pattern:
    """USD price formatiga mos regex: 12345 → r'USD[\\s]+12[,\\s]345'"""
    thousands = price // 1000
    remainder = price % 1000
    return re.compile(rf"USD[\s]+{thousands}[,\s]{remainder:03d}(?!\d)")


USAGE_CARD_TEST_IDS = {
    "Bids placed": "usage_bids_placed_card",
    "Bookings": "usage_bookings_card",
    "Fleet size": "usage_fleet_size_card",
    "Company roles": "usage_company_roles_card",
    "Company employees": "usage_company_employees_card",
}


def dismiss_cookie_banner(page: Page) -> None:
    """Dismiss cookie consent banner if visible."""
    btn = page.get_by_test_id("global_cookie_accept_button")
    if btn.is_visible():
        btn.click(force=True)


def pick_future_date(page: Page) -> None:
    """Select first available date from next month in calendar widget."""
    page.get_by_test_id("calendar_next_month_button").or_(
        page.get_by_role("button", name="Next month")
    ).first.click()
    day_cell = page.locator(
        "td[role='gridcell']:not([data-outside='true']) button:not([disabled])"
    ).first
    expect(day_cell).to_be_visible()
    day_cell.click()


def read_usage_counter(page: Page, label: str, limit: int) -> int:
    """Read a usage counter value from the Usage tab in profile."""
    page.goto(f"{APP_URL}/profile/root", wait_until="domcontentloaded")
    usage_link = page.get_by_test_id("sidebar_usage_link").or_(
        page.get_by_text("Usage", exact=True)
    ).first
    expect(usage_link).to_be_visible()
    usage_link.click()

    test_id = USAGE_CARD_TEST_IDS.get(label)
    if test_id:
        card = page.get_by_test_id(test_id)
    else:
        card = (
            page.locator("div")
            .filter(has_text=label)
            .filter(has_text=f"/ {limit}")
            .first
        )
    text = card.inner_text()
    match = re.search(rf"(\d+)\s*/\s*{limit}", text)
    assert match, f"'{label}' counter not found in card text:\n{text}"
    return int(match.group(1))


def navigate_to_loads(page: Page) -> None:
    """Navigate to /loads page via nav link or direct goto."""
    load_nav = page.get_by_test_id("top_nav_load_link").or_(
        page.get_by_role("link", name=re.compile(r"^Load$|^Груз$"))
    ).first
    if not load_nav.is_visible():
        page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")
    else:
        load_nav.click()
    page.wait_for_load_state("domcontentloaded")


def navigate_to_transport(page: Page) -> None:
    """Navigate to /transport page with blank-page fallback."""
    transport_nav = page.get_by_test_id("top_nav_transport_link").or_(
        page.get_by_role("link", name=re.compile(r"^Transport$|^Транспорт$"))
    ).first
    if transport_nav.is_visible():
        transport_nav.click()
    else:
        page.goto(f"{APP_URL}/transport", wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")


def create_load(load_owner: Page, price: int) -> None:
    """Create a load as load_owner with the given price.

    Form steps (2025-06 layout):
      Step 1: Route + load type + weight + date
      Step 2: Body (transport type)
      Step 3: Payment (price)
      Step 4: Review + publish
    """
    load_owner.get_by_test_id("global_add_button").click()
    load_owner.get_by_test_id("global_add_load_menu_item").click()
    expect(load_owner.get_by_test_id("loads_from_input")).to_be_visible()

    # Step 1 — Route & load
    load_owner.get_by_test_id("loads_from_input").fill("TASH")
    load_owner.get_by_text("Tashkent", exact=True).click()
    load_owner.get_by_test_id("loads_to_input").fill("DENA")
    load_owner.get_by_text("Denain", exact=True).click()

    load_owner.get_by_test_id("loads_load_type_select").click()
    load_owner.get_by_role("option", name="dovcha").click()

    load_owner.get_by_test_id("loads_weight_input").fill("12")

    load_owner.get_by_test_id("loads_date_button").click()
    pick_future_date(load_owner)

    dismiss_cookie_banner(load_owner)

    load_owner.get_by_test_id("loads_next_button").click()

    # Step 2 — Body
    expect(load_owner.get_by_test_id("loads_transport_type_select")).to_be_visible()
    load_owner.get_by_test_id("loads_transport_type_select").click()
    load_owner.get_by_role("option", name="Mega truck").click()
    load_owner.get_by_test_id("loads_next_button").click()

    # Step 3 — Payment
    expect(load_owner.get_by_test_id("loads_price_input")).to_be_visible()
    load_owner.get_by_test_id("loads_price_input").fill(str(price))
    load_owner.get_by_test_id("loads_next_button").click()

    # Step 4 — Publish
    publish_btn = load_owner.get_by_test_id("loads_publish_button")
    if publish_btn.is_visible():
        publish_btn.click()
    expect(load_owner).not_to_have_url(re.compile(r".*/create.*"))

    # Navigate away so the next create_load starts clean
    load_owner.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")


def place_bid_on_load(bidder: Page, price: int) -> None:
    """Find a load by price on /loads and place a bid."""
    navigate_to_loads(bidder)

    load_card = bidder.get_by_text(price_regex(price)).first
    expect(load_card).to_be_visible()
    load_card.click()

    bid_btn = bidder.get_by_test_id("bid_place_open_button").or_(
        bidder.get_by_role("button", name="Place a bid")
    ).first
    expect(bid_btn).to_be_visible()
    bid_btn.click()

    dismiss_cookie_banner(bidder)

    date_btn = bidder.get_by_test_id("bid_form_date_button").or_(
        bidder.get_by_role("button", name="Date")
    ).first
    expect(date_btn).to_be_visible()
    date_btn.click()
    pick_future_date(bidder)

    submit_btn = bidder.get_by_test_id("bid_form_submit_button").or_(
        bidder.get_by_role("button", name="Place a bid")
    ).last
    submit_btn.click()

    # Detect bid limit modal
    limit_modal = bidder.get_by_text("Limit reached")
    if limit_modal.is_visible():
        bidder.get_by_test_id("limit_modal_maybe_later_button").or_(
            bidder.get_by_role("button", name="Maybe later")
        ).first.click()
        pytest.fail("Bid limit reached — run reset_usage.py or use --reset-usage flag")

    bidder.wait_for_timeout(2000)


def create_load_and_place_bid(
    load_owner: Page, bidder: Page, price: str
) -> None:
    """Full flow: load_owner creates a load, bidder places a bid on it."""
    price_int = int(price)
    create_load(load_owner, price_int)
    place_bid_on_load(bidder, price_int)


def add_trailer(page: Page, index: int, prefix: str = "TRL") -> None:
    """Add a trailer in Fleet > Trailers tab."""
    page.goto(f"{APP_URL}/tms/fleet", wait_until="domcontentloaded")

    trailers_tab = page.get_by_test_id("fleet_trailers_tab")
    expect(trailers_tab).to_be_visible()
    trailers_tab.click()

    add_btn = page.get_by_test_id("fleet_add_trailer_button")
    expect(add_btn).to_be_visible()
    add_btn.click()

    country_select = page.get_by_test_id("fleet_country_select")
    expect(country_select).to_be_visible()
    country_select.click()
    page.get_by_role("option", name="United Arab Emirates").click()

    page.get_by_test_id("fleet_gov_number_input").click()
    page.get_by_test_id("fleet_gov_number_input").fill(f"{prefix}-{index:03d}")

    page.get_by_test_id("fleet_trailer_type_select").click()
    page.get_by_role("option", name="Trailer 1").click()

    page.get_by_test_id("fleet_year_select").click()
    page.get_by_role("option", name="2018").click()

    page.get_by_test_id("fleet_form_submit_button").click()
    page.wait_for_timeout(2000)


def create_role(page: Page, name: str) -> None:
    """Create a company role in Profile > Roles tab."""
    page.goto(f"{APP_URL}/profile/root", wait_until="domcontentloaded")

    roles_tab = page.get_by_test_id("profile_roles_tab")
    expect(roles_tab).to_be_visible()
    roles_tab.click()

    create_btn = page.get_by_test_id("roles_create_button")
    expect(create_btn).to_be_visible()
    create_btn.click()

    name_input = page.get_by_test_id("roles_name_input").or_(
        page.get_by_role("textbox", name="Role name")
    ).first
    expect(name_input).to_be_visible()
    name_input.click()
    name_input.fill(name)

    page.get_by_test_id("roles_submit_button").or_(
        page.get_by_role("button", name="Create role")
    ).first.click()
    page.wait_for_timeout(2000)


def invite_employee(page: Page, index: int, prefix: str = "emp") -> None:
    """Invite an employee in Profile > Users tab."""
    page.goto(f"{APP_URL}/profile/root", wait_until="domcontentloaded")

    users_tab = page.get_by_test_id("profile_users_tab")
    expect(users_tab).to_be_visible()
    users_tab.click()

    invite_btn = page.get_by_test_id("users_invite_button")
    expect(invite_btn).to_be_visible()
    invite_btn.click()

    email_input = page.get_by_test_id("users_invite_email_input").or_(
        page.get_by_role("textbox", name="Phone or Email")
    ).first
    expect(email_input).to_be_visible()
    email_input.fill(f"{prefix}_{index}@test.com")

    page.get_by_test_id("users_invite_role_select").or_(
        page.get_by_role("combobox", name="Role")
    ).first.click()
    page.get_by_role("option").first.click()

    page.get_by_test_id("users_send_invitation_button").or_(
        page.get_by_role("button", name="Send Invitation")
    ).first.click()
    page.wait_for_timeout(2000)
