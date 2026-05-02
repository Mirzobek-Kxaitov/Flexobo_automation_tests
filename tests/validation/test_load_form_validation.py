"""
Load yaratish formasini noto'g'ri/yetarli bo'lmagan ma'lumot bilan tekshirish.

Strategiya: form yetarli to'ldirilmagan bo'lsa, "Next" tugma Body step'ga
o'tkazmasligi kerak. Date'ga tegmaymiz (calendar widget'da o'zgaruvchan
state) — incremental fill bilan validatsiya'ni tekshiramiz.
"""
import allure
from playwright.sync_api import Page, expect
from pages.loads_page import LoadsPage


@allure.feature("Validation")
@allure.story("Load form: empty form blocks progress")
def test_empty_form_blocks_next(logged_in_broker: Page):
    """Bo'sh form: Next bosilsa Body step ochilmasligi kerak."""
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    logged_in_broker.wait_for_timeout(2000)

    loads.next_button.click(force=True, timeout=5000)
    expect(loads.body_step_heading).not_to_be_visible(timeout=3000)


@allure.feature("Validation")
@allure.story("Load form: missing weight blocks progress")
def test_missing_weight_blocks_next(logged_in_broker: Page):
    """From, To, Type to'ldirilgan, lekin weight bo'sh → Next blocked."""
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    logged_in_broker.wait_for_timeout(2000)

    loads.fill_from("Toshkent", "Tashkent, 100000, Uzbekistan")
    loads.fill_to("Termez", "Termez, Termiz District, Surxondaryo Province, Uzbekistan")
    loads.select_load_type("Metal aggregate")
    # weight to'ldirilmadi
    loads.accept_cookies_if_visible()

    loads.next_button.click(force=True, timeout=5000)
    expect(loads.body_step_heading).not_to_be_visible(timeout=3000)


@allure.feature("Validation")
@allure.story("Load form: zero weight blocks progress")
def test_zero_weight_blocks_next(logged_in_broker: Page):
    """Weight=0 — qabul qilinmasligi kerak."""
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    logged_in_broker.wait_for_timeout(2000)

    loads.fill_from("Toshkent", "Tashkent, 100000, Uzbekistan")
    loads.fill_to("Termez", "Termez, Termiz District, Surxondaryo Province, Uzbekistan")
    loads.select_load_type("Metal aggregate")
    loads.fill_weight("0")
    loads.accept_cookies_if_visible()

    loads.next_button.click(force=True, timeout=5000)
    expect(loads.body_step_heading).not_to_be_visible(timeout=3000)


@allure.feature("Validation")
@allure.story("Load form: negative weight blocks progress")
def test_negative_weight_blocks_next(logged_in_broker: Page):
    """Weight=-100 — manfiy qiymat qabul qilinmasligi kerak."""
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    logged_in_broker.wait_for_timeout(2000)

    loads.fill_from("Toshkent", "Tashkent, 100000, Uzbekistan")
    loads.fill_to("Termez", "Termez, Termiz District, Surxondaryo Province, Uzbekistan")
    loads.select_load_type("Metal aggregate")
    loads.fill_weight("-100")
    loads.accept_cookies_if_visible()

    loads.next_button.click(force=True, timeout=5000)
    expect(loads.body_step_heading).not_to_be_visible(timeout=3000)
