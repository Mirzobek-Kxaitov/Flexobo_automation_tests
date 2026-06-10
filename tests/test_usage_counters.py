"""
Usage sahifa counterlar testlari — limit metrikalari aktion bajarilganda
to'g'ri o'sayotganini tekshirish.

Strategiya: before/after pattern.
1. Action'dan oldin counter qiymatini o'qish (N)
2. Action'ni bajarish (masalan, bid yuborish)
3. Counter endi N+1 ekanligini tasdiqlash
"""
import os
import re
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _open_usage(page: Page) -> None:
    page.goto(f"{APP_URL}/profile/root", wait_until="domcontentloaded")
    usage_link = page.get_by_test_id("sidebar_usage_link").or_(
        page.get_by_text("Usage", exact=True)
    ).first
    expect(usage_link).to_be_visible(timeout=10000)
    usage_link.click()
    expect(page.get_by_test_id("usage_bids_placed_card")).to_be_visible(timeout=15000)


def _read_bids_placed_count(page: Page) -> int:
    _open_usage(page)
    card = page.get_by_test_id("usage_bids_placed_card")
    text = card.inner_text(timeout=10000)
    match = re.search(r"(\d+)\s*/\s*20", text)
    assert match, f"'Bids placed' formatda son topilmadi. Card matni:\n{text}"
    return int(match.group(1))


def _place_one_bid(page: Page) -> None:
    page.goto(f"{APP_URL}/loads", wait_until="domcontentloaded")

    be_first = page.get_by_text("Be first").first
    expect(be_first).to_be_visible(timeout=20000)
    be_first.click()

    bid_btn = page.get_by_test_id("bid_place_open_button")
    expect(bid_btn).to_be_visible(timeout=10000)
    bid_btn.click()
    expect(page.get_by_test_id("bid_form_container")).to_be_visible(timeout=10000)

    note = page.get_by_test_id("bid_form_note_input")
    if note.is_visible(timeout=2000):
        note.fill("Counter increment test bid")

    page.get_by_test_id("bid_form_submit_button").click()
    page.wait_for_timeout(3000)


@allure.feature("Usage Counter")
@allure.story("Bids placed counter increments by 1 after placing a bid")
@allure.severity(allure.severity_level.CRITICAL)
def test_bids_placed_counter_increments_by_one(free_broker: Page):
    page = free_broker
    page.set_default_timeout(60000)

    initial_count = _read_bids_placed_count(page)
    _place_one_bid(page)
    new_count = _read_bids_placed_count(page)

    assert new_count == initial_count + 1, (
        f"Bids placed counter aniq 1 ga ortishi kerak edi: "
        f"avval={initial_count}, hozir={new_count}, kutilgan={initial_count + 1}"
    )
