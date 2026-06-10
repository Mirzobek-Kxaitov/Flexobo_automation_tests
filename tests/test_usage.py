"""
Usage sahifa testlari — Free plan ruxsatlari va limitlari.

/usage sahifasi foydalanuvchining obunasi (subscription) holatini ko'rsatadi:
- Joriy reja (Current plan: Free)
- 9 ta metrika kartasi (Bids placed, Bookings, Fleet size va h.k.)
- Har birida joriy foydalanish va limit (masalan, 0 / 20)
- "Upgrade plan" tugmasi

Bu testlar Free plan uchun yozilgan. Reja o'zgarsa, FREE_PLAN_LIMITS
yangilanishi kerak.
"""
import os
import allure
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

ROLES = ["broker", "load_owner", "carrier", "owner_operator"]

# Free plan metrika kartalari va ularning limitlari (UI ko'rsatkichi)
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


def _open_usage(page: Page) -> Page:
    """Sidebar orqali Usage sahifasiga o'tish (direct goto SPA state'ni buzishi mumkin)."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)
    return page


@allure.feature("Usage")
@allure.story("Page accessible to all roles")
@pytest.mark.parametrize("role", ROLES)
def test_usage_page_accessible(request, role: str):
    """Usage sahifasi har 4 rol uchun ochiladi."""
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    _open_usage(page)
    expect(page.get_by_test_id("usage_page")).to_be_visible(timeout=10000)


@allure.feature("Usage")
@allure.story("Current plan: Free")
def test_current_plan_is_free(free_broker: Page):
    """Test foydalanuvchi Free planda ekanligini ko'rsatishi kerak."""
    _open_usage(free_broker)
    expect(free_broker.get_by_test_id("usage_current_plan_label")).to_contain_text(
        "Free", timeout=10000
    )


@allure.feature("Usage")
@allure.story("Upgrade plan button visible")
def test_upgrade_plan_button_visible(logged_in_broker: Page):
    """'Upgrade plan' tugmasi ko'rinadi (Free plan'dan yuqorilash imkoniyati)."""
    _open_usage(logged_in_broker)
    expect(logged_in_broker.get_by_test_id("usage_upgrade_plan_button")).to_be_visible(
        timeout=10000
    )


@allure.feature("Usage")
@allure.story("Free plan: metric card with correct limit")
@pytest.mark.parametrize("metric,limit", FREE_PLAN_LIMITS)
def test_free_plan_metric_with_limit(
    free_broker: Page, metric: str, limit: str
):
    """Har bir metrika kartasi label va Free plan limit qiymatini ko'rsatishi kerak."""
    _open_usage(free_broker)
    card = free_broker.get_by_test_id(metric)
    expect(card).to_be_visible(timeout=10000)
    expect(card).to_contain_text(limit)
