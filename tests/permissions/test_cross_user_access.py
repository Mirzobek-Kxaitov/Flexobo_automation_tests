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

from pages.loads_page import LoadsPage
from pages.trips_page import TripsPage

load_dotenv()
APP_URL = os.getenv("APP_URL")
BROKER_EMAIL = os.getenv("BROKER_EMAIL")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")
LOAD_OWNER_EMAIL = os.getenv("LOAD_OWNER_EMAIL")
LOAD_OWNER_PASSWORD = os.getenv("LOAD_OWNER_PASSWORD")

FORBIDDEN_REDIRECT_URL = f"{APP_URL}/profile/root"


def _login(page: Page, email: str, password: str):
    """
    Login helper — asosiy fixture'siz ham ishlaydi.
    Login muvaffaqiyatli bo'lganini /sign-in dan chiqib ketganligi orqali tasdiqlaymiz
    (turli rolelar /loads yoki /profile/root ga tushishi mumkin).
    """
    page.goto(f"{APP_URL}/sign-in?lang=en")
    page.get_by_test_id("login_email_input").fill(email)
    page.get_by_test_id("login_password_input").fill(password)
    page.get_by_test_id("login_submit_button").click()
    expect(page).not_to_have_url(re.compile(r".*sign-in.*"), timeout=15000)

    accept = page.get_by_test_id("global_cookie_accept_button")
    if accept.is_visible():
        accept.click()


def _logout(page: Page):
    """Profile dropdown orqali logout."""
    page.get_by_test_id("global_user_menu_button").click()
    page.get_by_test_id("global_logout_menu_item").or_(
        page.get_by_role("menuitem", name="Logout")
    ).first.click()
    page.get_by_test_id("global_logout_confirm_button").or_(
        page.get_by_text("Yes")
    ).first.click()
    expect(page).to_have_url(re.compile(r"sign-in|landing"), timeout=10000)


@allure.feature("Permissions")
@allure.story("Cross-user: load SAVE attack (defense in depth)")
@allure.severity(allure.severity_level.BLOCKER)
def test_load_owner_save_does_not_modify_brokers_load(page: Page):
    """
    Defense in depth verifikatsiyasi: edit sahifasi ochiq bo'lsa ham,
    backend SAVE ni rad etishi va broker'ning ma'lumoti o'zgarmasligi kerak.

    Hujum stsenariysi:
    1. Broker yuk yaratadi (weight=20, original).
    2. LoadOwner broker'ning edit URL'iga kiradi va weight=12345 deb save bosadi.
    3. Broker login qilib, list'ida HACK_WEIGHT YO'Q ekanini tasdiqlaymiz.

    PASSED: backend save'ni block qiladi (himoya ishlaydi).
    FAILED: real data manipulation — KRITIK BUG.
    """
    HACK_WEIGHT = "12345"

    # 1. Broker login va yuk yaratish
    _login(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/loads")
    page.wait_for_timeout(3000)
    LoadsPage(page).create_load(
        from_city="Toshkent",
        from_suggestion="Tashkent, 100000, Uzbekistan",
        to_city="Termez",
        to_suggestion="Termez, Termiz District, Surxondaryo Province, Uzbekistan",
        load_type="Metal aggregate",
        weight="20",
        body_type="Mega truck",
        price="1000",
    ).expect_load_created()

    # 2. Edit URL'ni saqlaymiz
    page.goto(f"{APP_URL}/profile-load")
    page.wait_for_timeout(2000)
    page.get_by_role("button").nth(4).click()
    page.wait_for_timeout(500)
    page.get_by_role("menuitem", name="Change").click()
    expect(page).to_have_url(re.compile(r".*/loads/[a-f0-9-]+/edit.*"), timeout=10000)
    brokers_edit_url = page.url

    # 3. Logout + cookie tozalash
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    _logout(page)
    page.context.clear_cookies()

    # 4. LoadOwner login → broker'ning edit URL'iga goto → save attack
    _login(page, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD)
    page.goto(brokers_edit_url)
    page.wait_for_timeout(3000)

    loads = LoadsPage(page)
    try:
        loads.weight_input.fill(HACK_WEIGHT)
        loads.click_next()       # Step 1 → Body
        loads.click_next()       # Body → Payment
        loads.click_next()       # Payment → Confirmation
        loads.publish()          # Save
        page.wait_for_timeout(3000)
    except Exception:
        # UI yoki backend xato bersa — bu yaxshi (himoya ishlaydi)
        pass

    # 5. Broker'ga qaytib, ma'lumoti o'zgarmaganini tasdiqlash
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    if page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).is_visible():
        try:
            _logout(page)
        except Exception:
            pass
    page.context.clear_cookies()

    _login(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/profile-load")
    page.wait_for_timeout(3000)

    # HACK_WEIGHT broker'ning yuklarida YO'Q bo'lishi kerak
    expect(page.get_by_text(HACK_WEIGHT).first).not_to_be_visible(timeout=5000)


@allure.feature("Permissions")
@allure.story("Cross-user: my loads list isolation")
@allure.severity(allure.severity_level.CRITICAL)
def test_load_owner_does_not_see_brokers_loads_in_list(page: Page):
    """
    Broker yuk yaratadi → logout.
    LoadOwner login qilib, "My Loads" sahifasiga boradi.
    Kutish: Broker'ning yuki LoadOwner'ning ro'yxatida KO'RINMAYDI.
    """
    # 1. Broker login + yuk yaratish (unique price bilan, identifikatsiya uchun)
    UNIQUE_PRICE = "7777"
    _login(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/loads")
    page.wait_for_timeout(3000)
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

    # 2. Logout
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    _logout(page)
    page.context.clear_cookies()

    # 3. LoadOwner login + My Loads ro'yxatiga o'tish
    _login(page, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD)
    page.goto(f"{APP_URL}/profile-load")
    page.wait_for_timeout(3000)

    # 4. Broker yaratgan yuk (UNIQUE_PRICE) LoadOwner'ning ro'yxatida ko'rinmasligi kerak
    expect(page.get_by_text(UNIQUE_PRICE).first).not_to_be_visible(timeout=5000)


@allure.feature("Permissions")
@allure.story("Cross-user: trip SAVE attack (defense in depth)")
@allure.severity(allure.severity_level.BLOCKER)
def test_load_owner_save_does_not_modify_brokers_trip(page: Page):
    """
    Defense in depth verifikatsiyasi — trip uchun (load uchun bilamiz, trip ham bormi?).

    Hujum stsenariysi:
    1. Broker trip yaratadi (price=1200, original).
    2. LoadOwner broker'ning trip edit URL'iga kiradi va price=99999 deb save bosadi.
    3. Broker login qilib, list'ida HACK_PRICE YO'Q ekanini tasdiqlaymiz.

    PASSED: backend save'ni block qiladi.
    FAILED: real data manipulation — KRITIK BUG.
    """
    HACK_PRICE = "99999"

    # 1. Broker login va trip yaratish
    _login(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/loads")
    page.wait_for_timeout(3000)
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

    # 2. Edit URL'ni saqlaymiz
    page.goto(f"{APP_URL}/profile-trips")
    page.wait_for_timeout(2000)
    page.get_by_role("button").nth(4).click()
    page.wait_for_timeout(500)
    page.get_by_role("menuitem", name="Change").click()
    page.wait_for_timeout(2000)
    brokers_trip_edit_url = page.url

    # 3. Logout + cookie tozalash
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    _logout(page)
    page.context.clear_cookies()

    # 4. LoadOwner login → broker'ning trip edit URL'iga goto → save attack
    _login(page, LOAD_OWNER_EMAIL, LOAD_OWNER_PASSWORD)
    page.goto(brokers_trip_edit_url)
    page.wait_for_timeout(3000)

    trips = TripsPage(page)
    try:
        trips.click_next()       # Step 1 → Payment
        trips.fill_price(HACK_PRICE)
        trips.click_next()       # Save / Confirm
        page.wait_for_timeout(3000)
    except Exception:
        # UI yoki backend xato bersa — bu yaxshi
        pass

    # 5. Broker'ga qaytib, ma'lumoti o'zgarmaganini tasdiqlash
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    if page.locator("button[data-slot='dropdown-menu-trigger']").nth(3).is_visible():
        try:
            _logout(page)
        except Exception:
            pass
    page.context.clear_cookies()

    _login(page, BROKER_EMAIL, BROKER_PASSWORD)
    page.goto(f"{APP_URL}/profile-trips")
    page.wait_for_timeout(3000)

    # HACK_PRICE broker'ning trip'larida YO'Q bo'lishi kerak
    expect(page.get_by_text(HACK_PRICE).first).not_to_be_visible(timeout=5000)
