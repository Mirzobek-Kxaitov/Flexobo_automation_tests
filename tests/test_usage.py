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
    ("Bids placed", "/ 20"),
    ("Bookings", "/ 5"),
    ("Contacts viewed", "/ Unlimited"),
    ("Team members", "/ Unlimited"),
    ("Storage used", "/ Unlimited"),
    ("Fleet size", "/ 5"),
    ("Active transport", "/ 3"),
    ("Company roles", "/ 1"),
    ("Company employees", "/ 2"),
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
    # Sahifa sarlavhasi va subtitle ko'rinishi kerak
    expect(
        page.get_by_text("Monitor your subscription usage and limits")
    ).to_be_visible(timeout=10000)


@allure.feature("Usage")
@allure.story("Current plan: Free")
def test_current_plan_is_free(logged_in_broker: Page):
    """Test foydalanuvchi Free planda ekanligini ko'rsatishi kerak."""
    _open_usage(logged_in_broker)
    expect(
        logged_in_broker.get_by_text("Current plan: Free")
    ).to_be_visible(timeout=10000)


@allure.feature("Usage")
@allure.story("Upgrade plan button visible")
def test_upgrade_plan_button_visible(logged_in_broker: Page):
    """'Upgrade plan' tugmasi ko'rinadi (Free plan'dan yuqorilash imkoniyati)."""
    _open_usage(logged_in_broker)
    expect(
        logged_in_broker.get_by_role("button", name="Upgrade plan")
    ).to_be_visible(timeout=10000)


@allure.feature("Usage")
@allure.story("Free plan: metric card with correct limit")
@pytest.mark.parametrize("metric,limit", FREE_PLAN_LIMITS)
def test_free_plan_metric_with_limit(
    logged_in_broker: Page, metric: str, limit: str
):
    """Har bir metrika kartasi label va Free plan limit qiymatini ko'rsatishi kerak."""
    _open_usage(logged_in_broker)
    # Karta — div ichida ham metric label, ham limit qiymati bo'lishi kerak
    card = (
        logged_in_broker.locator("div")
        .filter(has_text=metric)
        .filter(has_text=limit)
        .first
    )
    expect(card).to_be_visible(timeout=10000)
