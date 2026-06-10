#!/usr/bin/env python3
"""Audit live pages for required QA data-testid attributes."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright


load_dotenv()


@dataclass(frozen=True)
class TestIdCheck:
    name: str
    url_env: str
    path: str
    test_ids: tuple[str, ...]
    role: str | None = None
    action: str | None = None
    invalid_login: bool = False


CHECKS: dict[str, TestIdCheck] = {
    "login": TestIdCheck(
        name="login",
        url_env="APP_URL",
        path="/sign-in?lang=en",
        test_ids=(
            "login_email_input",
            "login_password_input",
            "login_submit_button",
            "login_error_message",
        ),
        invalid_login=True,
    ),
    "landing": TestIdCheck(
        name="landing",
        url_env="BASE_URL",
        path="",
        test_ids=(
            "landing_sign_in_button",
            "landing_search_from_input",
            "landing_search_to_input",
            "landing_search_date_button",
            "landing_search_button",
        ),
    ),
    "profile": TestIdCheck(
        name="profile",
        url_env="APP_URL",
        path="/profile/root",
        role="broker",
        test_ids=(
            "global_user_menu_button",
            "sidebar_profile_link",
            "sidebar_my_loads_link",
            "sidebar_my_trips_link",
            "sidebar_fleet_link",
            "sidebar_my_bids_link",
            "sidebar_received_bids_link",
            "sidebar_usage_link",
            "profile_roles_tab",
            "profile_users_tab",
        ),
    ),
    "add_menu": TestIdCheck(
        name="add_menu",
        url_env="APP_URL",
        path="/profile/root",
        role="broker",
        action="open_add_menu",
        test_ids=(
            "global_add_button",
            "global_add_load_menu_item",
            "global_add_transport_menu_item",
        ),
    ),
}

add_menu_visible_ids = {
    "broker": ("global_add_load_menu_item", "global_add_transport_menu_item"),
    "load_owner": ("global_add_load_menu_item",),
    "carrier": ("global_add_transport_menu_item",),
    "owner_operator": ("global_add_transport_menu_item",),
}

for role_name, visible_ids in add_menu_visible_ids.items():
    CHECKS[f"add_menu_{role_name}"] = TestIdCheck(
        name=f"add_menu_{role_name}",
        url_env="APP_URL",
        path="/profile/root",
        role=role_name,
        action="open_add_menu",
        test_ids=("global_add_button", *visible_ids),
    )

for role_name in ("broker", "load_owner", "carrier", "owner_operator"):
    CHECKS[f"logout_menu_{role_name}"] = TestIdCheck(
        name=f"logout_menu_{role_name}",
        url_env="APP_URL",
        path="/profile/root",
        role=role_name,
        action="open_user_menu",
        test_ids=(
            "global_user_menu_button",
            "global_logout_menu_item",
        ),
    )
    CHECKS[f"logout_confirm_{role_name}"] = TestIdCheck(
        name=f"logout_confirm_{role_name}",
        url_env="APP_URL",
        path="/profile/root",
        role=role_name,
        action="open_logout_confirm",
        test_ids=("global_logout_confirm_button",),
    )

for role_name in ("broker", "carrier", "owner_operator"):
    CHECKS[f"loads_board_{role_name}"] = TestIdCheck(
        name=f"loads_board_{role_name}",
        url_env="APP_URL",
        path="/loads",
        role=role_name,
        test_ids=(
            "loads_search_from_input",
            "loads_search_to_input",
            "loads_search_button",
            "loads_filter_button",
        ),
    )

CHECKS["loads_filter_broker"] = TestIdCheck(
    name="loads_filter_broker",
    url_env="APP_URL",
    path="/loads",
    role="broker",
    action="open_loads_filter",
    test_ids=(
        "loads_filter_panel",
        "loads_filter_apply_button",
        "loads_filter_reset_button",
    ),
)

fleet_visible_ids = {
    "broker": (
        "fleet_page",
        "fleet_trucks_tab",
        "fleet_trailers_tab",
        "fleet_add_truck_button",
        "fleet_add_trailer_button",
    ),
    "carrier": (
        "fleet_page",
        "fleet_trucks_tab",
        "fleet_trailers_tab",
        "fleet_add_truck_button",
        "fleet_add_trailer_button",
    ),
    "owner_operator": (
        "fleet_page",
        "fleet_trailers_tab",
        "fleet_add_trailer_button",
    ),
}

for role_name, visible_ids in fleet_visible_ids.items():
    CHECKS[f"fleet_{role_name}"] = TestIdCheck(
        name=f"fleet_{role_name}",
        url_env="APP_URL",
        path="/tms/fleet",
        role=role_name,
        test_ids=visible_ids,
    )

my_bids_tab_ids = (
    "my_bids_page",
    "my_bids_all_tab",
    "my_bids_pending_tab",
    "my_bids_accepted_tab",
    "my_bids_rejected_tab",
    "my_bids_on_the_way_tab",
    "my_bids_delivered_tab",
)

for role_name in ("broker", "load_owner", "carrier", "owner_operator"):
    CHECKS[f"my_bids_{role_name}"] = TestIdCheck(
        name=f"my_bids_{role_name}",
        url_env="APP_URL",
        path="/my-bids",
        role=role_name,
        test_ids=my_bids_tab_ids,
    )

CHECKS["bid_detail_carrier"] = TestIdCheck(
    name="bid_detail_carrier",
    url_env="APP_URL",
    path="/loads",
    role="carrier",
    action="open_first_load_detail",
    test_ids=("bid_place_open_button",),
)

CHECKS["bid_form_carrier"] = TestIdCheck(
    name="bid_form_carrier",
    url_env="APP_URL",
    path="/loads",
    role="carrier",
    action="open_bid_form",
    test_ids=(
        "bid_form_container",
        "bid_form_note_input",
        "bid_form_date_button",
        "bid_form_submit_button",
        "bid_form_cancel_button",
    ),
)

for role_name in ("broker", "owner_operator"):
    CHECKS[f"bid_detail_{role_name}"] = TestIdCheck(
        name=f"bid_detail_{role_name}",
        url_env="APP_URL",
        path="/loads",
        role=role_name,
        action="open_first_load_detail",
        test_ids=("bid_place_open_button",),
    )
    CHECKS[f"bid_form_{role_name}"] = TestIdCheck(
        name=f"bid_form_{role_name}",
        url_env="APP_URL",
        path="/loads",
        role=role_name,
        action="open_bid_form",
        test_ids=(
            "bid_form_container",
            "bid_form_note_input",
            "bid_form_date_button",
            "bid_form_submit_button",
            "bid_form_cancel_button",
        ),
    )

CHECKS["trips_create_broker"] = TestIdCheck(
    name="trips_create_broker",
    url_env="APP_URL",
    path="/trips/create",
    role="broker",
    test_ids=(
        "trips_transport_select",
        "trips_unit_select",
        "trips_volume_input",
        "trips_loading_input",
        "trips_loading_radius_input",
        "trips_unloading_input",
        "trips_unloading_radius_input",
        "trips_next_button",
    ),
)

CHECKS["loads_create_broker"] = TestIdCheck(
    name="loads_create_broker",
    url_env="APP_URL",
    path="/loads",
    role="broker",
    action="open_load_create",
    test_ids=(
        "loads_from_input",
        "loads_to_input",
        "loads_load_type_select",
        "loads_date_button",
        "loads_weight_input",
        "loads_next_button",
    ),
)

CHECKS["loads_calendar_broker"] = TestIdCheck(
    name="loads_calendar_broker",
    url_env="APP_URL",
    path="/loads",
    role="broker",
    action="open_load_calendar",
    test_ids=("calendar_next_month_button",),
)

CHECKS["usage_broker"] = TestIdCheck(
    name="usage_broker",
    url_env="APP_URL",
    path="/profile/root",
    role="broker",
    action="open_usage_tab",
    test_ids=(
        "usage_page",
        "usage_current_plan_label",
        "usage_upgrade_plan_button",
        "usage_bids_placed_card",
        "usage_bookings_card",
        "usage_contacts_viewed_card",
        "usage_team_members_card",
        "usage_storage_used_card",
        "usage_fleet_size_card",
        "usage_company_roles_card",
        "usage_company_employees_card",
    ),
)

usage_counter_ids = {
    "broker": (
        "usage_bids_placed_card",
        "usage_bookings_card",
        "usage_fleet_size_card",
        "usage_company_roles_card",
    ),
    "load_owner": (
        "usage_bids_placed_card",
        "usage_company_roles_card",
    ),
    "carrier": (
        "usage_bids_placed_card",
        "usage_fleet_size_card",
        "usage_company_roles_card",
        "usage_company_employees_card",
    ),
    "owner_operator": (
        "usage_bids_placed_card",
        "usage_active_transport_card",
    ),
}

for role_name, visible_ids in usage_counter_ids.items():
    CHECKS[f"usage_counters_{role_name}"] = TestIdCheck(
        name=f"usage_counters_{role_name}",
        url_env="APP_URL",
        path="/profile/root",
        role=role_name,
        action="open_usage_tab",
        test_ids=visible_ids,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit live data-testid coverage.")
    parser.add_argument(
        "checks",
        nargs="*",
        default=sorted(CHECKS),
        help=f"Checks to run. Available: {', '.join(sorted(CHECKS))}",
    )
    parser.add_argument("--headed", action="store_true", help="Run browser headed.")
    return parser.parse_args()


def base_url(check: TestIdCheck) -> str:
    value = os.getenv(check.url_env)
    if not value:
        raise RuntimeError(f"{check.url_env} must be set in .env")
    return value.rstrip("/")


def run_invalid_login(page: Page) -> None:
    page.get_by_test_id("login_email_input").fill("wrong@example.com")
    page.get_by_test_id("login_password_input").fill("wrongpass123")
    page.get_by_test_id("login_submit_button").click()
    page.wait_for_timeout(1500)


def env_credentials(role: str) -> tuple[str, str]:
    prefixes = {
        "broker": "BROKER",
        "load_owner": "LOAD_OWNER",
        "carrier": "CARRIER",
        "owner_operator": "OWNER_OPERATOR",
    }
    prefix = prefixes[role]
    email = os.getenv(f"{prefix}_EMAIL")
    password = os.getenv(f"{prefix}_PASSWORD")
    if not email or not password:
        raise RuntimeError(f"{prefix}_EMAIL/{prefix}_PASSWORD must be set in .env")
    return email, password


def login_as(page: Page, role: str) -> None:
    email, password = env_credentials(role)
    page.goto(f"{base_url(CHECKS['login'])}/sign-in?lang=en", wait_until="domcontentloaded")
    page.get_by_test_id("login_email_input").fill(email)
    page.get_by_test_id("login_password_input").fill(password)
    page.get_by_test_id("login_submit_button").click()
    page.wait_for_function("!window.location.href.includes('sign-in')", timeout=15000)

    accept_button = page.get_by_test_id("global_cookie_accept_button")
    if accept_button.is_visible(timeout=1000):
        accept_button.click(force=True)


def open_load_detail_with_bid_button(page: Page) -> None:
    candidates = page.get_by_text("Be first")
    count = min(candidates.count(), 5)
    if count == 0:
        raise RuntimeError("No 'Be first' load candidates found")

    for index in range(count):
        candidates.nth(index).click()
        page.wait_for_timeout(1000)
        if page.get_by_test_id("bid_place_open_button").is_visible(timeout=1500):
            return
        page.go_back(wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

    raise RuntimeError("No load detail with bid_place_open_button found")


def run_action(page: Page, action: str | None) -> None:
    if action == "open_add_menu":
        page.get_by_test_id("global_add_button").click()
        page.wait_for_timeout(300)
    elif action == "open_user_menu":
        page.get_by_test_id("global_user_menu_button").click()
        page.wait_for_timeout(300)
    elif action == "open_logout_confirm":
        page.get_by_test_id("global_user_menu_button").click()
        page.wait_for_timeout(300)
        page.get_by_test_id("global_logout_menu_item").click()
        page.wait_for_timeout(300)
    elif action == "open_loads_filter":
        page.get_by_test_id("loads_filter_button").click()
        page.wait_for_timeout(500)
    elif action == "open_first_load_detail":
        open_load_detail_with_bid_button(page)
    elif action == "open_bid_form":
        open_load_detail_with_bid_button(page)
        page.get_by_test_id("bid_place_open_button").click()
        page.wait_for_timeout(500)
    elif action == "open_load_create":
        page.get_by_test_id("global_add_button").click()
        page.wait_for_timeout(300)
        page.get_by_test_id("global_add_load_menu_item").click()
        page.wait_for_timeout(2500)
    elif action == "open_load_calendar":
        page.get_by_test_id("global_add_button").click()
        page.wait_for_timeout(300)
        page.get_by_test_id("global_add_load_menu_item").click()
        page.wait_for_timeout(2500)
        page.get_by_test_id("loads_date_button").click()
        page.wait_for_timeout(300)
    elif action == "open_usage_tab":
        page.wait_for_timeout(2000)
        page.get_by_test_id("sidebar_usage_link").or_(
            page.get_by_text("Usage", exact=True)
        ).first.click()
        page.wait_for_timeout(2500)


def audit_check(page: Page, check: TestIdCheck) -> list[str]:
    if check.role:
        login_as(page, check.role)

    page.goto(f"{base_url(check)}{check.path}", wait_until="domcontentloaded")
    page.wait_for_timeout(500)

    if check.invalid_login:
        run_invalid_login(page)

    action_error: str | None = None
    try:
        run_action(page, check.action)
    except Exception as exc:  # noqa: BLE001 - audit should report missing UI, not abort.
        first_line = str(exc).splitlines()[0] if str(exc) else type(exc).__name__
        action_error = f"{type(exc).__name__}: {first_line}"

    missing: list[str] = []
    print(f"\n[{check.name}] {page.url}")
    if action_error:
        print(f"  ACTION_FAILED {check.action}: {action_error}")
    for test_id in check.test_ids:
        count = page.get_by_test_id(test_id).count()
        status = "OK" if count > 0 else "MISSING"
        print(f"  {status:7} {test_id} ({count})")
        if count == 0:
            missing.append(test_id)
    return missing


def main() -> int:
    args = parse_args()
    unknown = [name for name in args.checks if name not in CHECKS]
    if unknown:
        raise RuntimeError(f"Unknown checks: {', '.join(unknown)}")

    all_missing: dict[str, list[str]] = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        for name in args.checks:
            context = browser.new_context()
            page = context.new_page()
            missing = audit_check(page, CHECKS[name])
            context.close()
            if missing:
                all_missing[name] = missing
        browser.close()

    if all_missing:
        print("\nMissing data-testid values:")
        for name, missing in all_missing.items():
            print(f"  {name}: {', '.join(missing)}")
        return 1

    print("\nAll audited data-testid values are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
