"""
Cross-user authorization testlari.

Bir user yaratgan resurs (load/trip) — boshqa user uni tahrir qila olmasligi
yoki URL orqali to'g'ridan-to'g'ri kira olmasligi kerak.

Bu eng muhim xavfsizlik testlari — agar bug bo'lsa, GDPR/data leak bo'lishi mumkin.
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

from conftest import login_as
from pages.loads_page import LoadsPage
from pages.trips_page import TripsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")
BROKER_EMAIL = os.getenv("BROKER_EMAIL")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")
LOAD_OWNER_EMAIL = os.getenv("LOAD_OWNER_EMAIL")
LOAD_OWNER_PASSWORD = os.getenv("LOAD_OWNER_PASSWORD")


def _logout(page: Page):
    page.get_by_test_id("global_user_menu_button").click()
    page.get_by_test_id("global_logout_menu_item").click()
    page.get_by_test_id("global_logout_confirm_button").click()
    expect(page).to_have_url(re.compile(r"sign-in|landing"))


def _switch_user(page: Page, email: str, password: str):
    """Logout current user, clear cookies, login as new user."""
    _logout(page)
    page.context.clear_cookies()
    login_as(page, email, password)


@allure.feature("Permissions")
@allure.story("Cross-user: load SAVE attack (defense in depth)")
@allure.severity(allure.severity_level.BLOCKER)
def test_load_owner_save_does_not_modify_brokers_load(page: Page):
    """
    Defense in depth: edit sahifasi ochiq bo'lsa ham, backend SAVE ni
    rad etishi va broker'ning ma'lumoti o'zgarmasligi kerak.

    1. Broker yuk yaratadi (weight=20).
    2. LoadOwner broker'ning edit URL'iga kirib weight=12345 qilib save bosadi.
    3. Broker login qilib, original weight saqlanganini tasdiqlaydi.
    """
    HACK_WEIGHT = "12345"
    ORIGINAL_WEIGHT = "20"

    # 1. Broker login va yuk yaratish
    login_as(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    LoadsPage(page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight=ORIGINAL_WEIGHT,
        body_type="Mega truck",
        price="1000",
    ).expect_load_created()

    # 2. Edit URL'ni saqlaymiz
    page.goto(f"{APP_URL}/profile-load")
    page.wait_for_load_state("domcontentloaded")
    LoadsPage(page).click_change_on_first_load()
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]+/edit.*"))
    brokers_edit_url = page.url

    # 3. Switch to LoadOwner
    _switch_user(page, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD)

    # 4. Hujum: broker'ning edit URL'iga goto
    page.goto(brokers_edit_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # Agar backend URL darajasida himoya qilsa (redirect) — bu ham yaxshi
    on_edit_page = re.search(r"/loads/[a-f0-9-]+/edit", page.url)
    if on_edit_page and page.get_by_test_id("loads_weight_input").is_visible():
        # Edit forma ochiq — hujumni urinib ko'ramiz
        loads = LoadsPage(page)
        loads.weight_input.fill(HACK_WEIGHT)
        loads.click_next()
        expect(loads.price_input).to_be_visible()
        loads.click_next()
        if loads.publish_button.is_visible():
            loads.publish()
        page.wait_for_timeout(3000)

    # 5. Switch back to broker and verify
    _switch_user(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/profile-load")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # POSITIVE: page loaded with actual content
    page_text = page.locator("body").inner_text()
    assert len(page_text.strip()) > 50, \
        f"Profile-load sahifasi bo'sh yoki yuklanmadi: {page_text[:200]}"

    # NEGATIVE: HACK_WEIGHT must NOT appear in broker's loads
    expect(page.get_by_text(HACK_WEIGHT).first).not_to_be_visible()


@allure.feature("Permissions")
@allure.story("Cross-user: my loads list isolation")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_does_not_see_brokers_loads_in_list(page: Page):
    """
    Broker yuk yaratadi → LoadOwner login qilganda broker'ning yuki
    "My Loads" ro'yxatida ko'rinmasligi kerak.
    """
    import random
    UNIQUE_PRICE = str(random.randint(40000, 49999))

    # 1. Broker login + yuk yaratish
    login_as(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    LoadsPage(page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        body_type="Mega truck",
        price=UNIQUE_PRICE,
    ).expect_load_created()

    # 2. Switch to LoadOwner
    _switch_user(page, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD)

    # 3. Navigate to My Loads
    page.goto(f"{APP_URL}/profile-load")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # POSITIVE: page loaded with content
    page_text = page.locator("body").inner_text()
    assert len(page_text.strip()) > 50, \
        f"Profile-load sahifasi bo'sh yoki yuklanmadi: {page_text[:200]}"

    # NEGATIVE: broker's load must NOT appear in load_owner's list
    expect(page.get_by_text(UNIQUE_PRICE).first).not_to_be_visible()


@allure.feature("Permissions")
@allure.story("Cross-user: trip SAVE attack (defense in depth)")
@allure.severity(allure.severity_level.BLOCKER)
def test_load_owner_save_does_not_modify_brokers_trip(page: Page):
    """
    Defense in depth — trip uchun.

    1. Broker trip yaratadi (price=1200).
    2. LoadOwner broker'ning trip edit URL'iga kirib price=99999 qilib save bosadi.
    3. Broker login qilib, original price saqlanganini tasdiqlaydi.
    """
    HACK_PRICE = "99999"

    # 1. Broker login va trip yaratish
    login_as(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    TripsPage(page).create_trip(
        transport="Trailer 1",
        volume=10,
        loading_city="tashkent",
        loading_suggestion="Tashkent",
        loading_radius=12,
        unloading_city="denov",
        unloading_suggestion="Denov District",
        unloading_radius=12,
        price=1200,
    )

    # 2. Edit URL saqlaymiz
    page.goto(f"{APP_URL}/profile-trips")
    page.wait_for_load_state("domcontentloaded")
    TripsPage(page).click_change_on_first_trip()
    brokers_trip_edit_url = page.url

    # 3. Switch to LoadOwner
    _switch_user(page, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD)

    # 4. Hujum: broker'ning trip edit URL'iga goto
    page.goto(brokers_trip_edit_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # Agar backend URL darajasida himoya qilsa — bu ham yaxshi
    on_edit_page = re.search(r"/transport/[a-f0-9-]+/edit", page.url)
    if on_edit_page:
        trips = TripsPage(page)
        trips.click_next()
        trips.fill_price(HACK_PRICE)
        trips.click_next()
        page.wait_for_timeout(3000)

    # 5. Switch back to broker and verify
    _switch_user(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/profile-trips")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # POSITIVE: page loaded with content va ma'lumot bor
    page_text = page.locator("body").inner_text()
    assert len(page_text.strip()) > 50, \
        f"Profile-trips sahifasi bo'sh yoki yuklanmadi: {page_text[:200]}"

    # NEGATIVE: HACK_PRICE must NOT appear in broker's trips
    expect(page.get_by_text(HACK_PRICE).first).not_to_be_visible()
