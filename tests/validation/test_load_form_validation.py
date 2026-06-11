"""
Load form validation — Next button should not advance when required fields are missing.
"""
import allure
from playwright.sync_api import Page, expect
from pages.loads_page import LoadsPage


@allure.feature("Validation")
@allure.story("Load form: empty form blocks progress")
def test_empty_form_blocks_next(logged_in_broker: Page):
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    expect(loads.from_input).to_be_visible()

    loads.next_button.click()
    expect(loads.body_step_heading).not_to_be_visible()


@allure.feature("Validation")
@allure.story("Load form: missing weight blocks progress")
def test_missing_weight_blocks_next(logged_in_broker: Page):
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    expect(loads.from_input).to_be_visible()

    loads.fill_from("Toshkent", "Tashkent, 100000, Uzbekistan")
    loads.fill_to("Termez", "Termez, Termiz District, Surxondaryo Province, Uzbekistan")
    loads.select_load_type("Metal aggregate")
    loads.accept_cookies_if_visible()

    loads.next_button.click()
    expect(loads.body_step_heading).not_to_be_visible()


@allure.feature("Validation")
@allure.story("Load form: zero weight blocks progress")
def test_zero_weight_blocks_next(logged_in_broker: Page):
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    expect(loads.from_input).to_be_visible()

    loads.fill_from("Toshkent", "Tashkent, 100000, Uzbekistan")
    loads.fill_to("Termez", "Termez, Termiz District, Surxondaryo Province, Uzbekistan")
    loads.select_load_type("Metal aggregate")
    loads.fill_weight("0")
    loads.accept_cookies_if_visible()

    loads.next_button.click()
    expect(loads.body_step_heading).not_to_be_visible()


@allure.feature("Validation")
@allure.story("Load form: negative weight blocks progress")
def test_negative_weight_blocks_next(logged_in_broker: Page):
    loads = LoadsPage(logged_in_broker)
    loads.open_create_load_form()
    expect(loads.from_input).to_be_visible()

    loads.fill_from("Toshkent", "Tashkent, 100000, Uzbekistan")
    loads.fill_to("Termez", "Termez, Termiz District, Surxondaryo Province, Uzbekistan")
    loads.select_load_type("Metal aggregate")
    loads.fill_weight("-100")
    loads.accept_cookies_if_visible()

    loads.next_button.click()
    expect(loads.body_step_heading).not_to_be_visible()
