"""
Usage sahifa testlari — Free plan ruxsatlari va limitlari.
"""
import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from pages.usage_page import UsagePage

load_dotenv()
APP_URL = os.getenv("APP_URL")

ROLES = ["broker", "load_owner", "carrier", "owner_operator"]

FREE_PLAN_LIMITS = [
    ("usage_bids_placed_card", "/ 20"),
    ("usage_bookings_card", "/ 5"),
    ("usage_contacts_viewed_card", "/ Unlimited"),
    ("usage_team_members_card", "/ Unlimited"),
    ("usage_storage_used_card", "/ Unlimited"),
    ("usage_fleet_size_card", "/ 5"),
    ("usage_company_roles_card", "/ 1"),
    ("usage_company_employees_card", "/ 2"),
]


@allure.feature("Usage")
@allure.story("Page accessible to all roles")
@pytest.mark.parametrize("role", ROLES)
def test_usage_page_accessible(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    UsagePage(page).open(APP_URL).expect_visible()


@allure.feature("Usage")
@allure.story("Current plan: Free")
def test_current_plan_is_free(free_broker: Page):
    UsagePage(free_broker).open(APP_URL).expect_plan("Free")


@allure.feature("Usage")
@allure.story("Upgrade plan button visible")
def test_upgrade_plan_button_visible(logged_in_broker: Page):
    UsagePage(logged_in_broker).open(APP_URL).expect_upgrade_button_visible()


@allure.feature("Usage")
@allure.story("Free plan: metric card with correct limit")
@pytest.mark.parametrize("metric,limit", FREE_PLAN_LIMITS)
def test_free_plan_metric_with_limit(free_broker: Page, metric: str, limit: str):
    UsagePage(free_broker).open(APP_URL).expect_card_has_limit(metric, limit)
