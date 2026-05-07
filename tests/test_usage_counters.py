"""
Usage sahifa counterlar testlari — limit metrikalari aktion bajarilganda
to'g'ri o'sayotganini tekshirish.

Strategiya: before/after pattern.
1. Action'dan oldin counter qiymatini o'qish (N)
2. Action'ni bajarish (masalan, bid yuborish)
3. Counter endi N+1 ekanligini tasdiqlash

Bu testlar broker (Free plan) uchun yozilgan, chunki broker'da real
limitlar bor (Bids placed / 20).
"""
import os
import re
import allure
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")


def _open_usage(page: Page) -> None:
    """Sidebar orqali Usage sahifasiga o'tish."""
    page.goto(f"{APP_URL}/profile/root")
    page.wait_for_timeout(2000)
    page.get_by_text("Usage", exact=True).first.click()
    page.wait_for_timeout(3000)


def _read_bids_placed_count(page: Page) -> int:
    """
    Usage sahifasidan 'Bids placed' kartasidagi joriy sonni o'qish.
    Free plan format: 'X / 20', funksiya X ni qaytaradi.
    """
    _open_usage(page)
    card = (
        page.locator("div")
        .filter(has_text="Bids placed")
        .filter(has_text="/ 20")
        .first
    )
    text = card.inner_text(timeout=10000)
    match = re.search(r"(\d+)\s*/\s*20", text)
    assert match, f"'Bids placed' formatda son topilmadi. Card matni:\n{text}"
    return int(match.group(1))


def _place_one_bid(page: Page) -> None:
    """/loads sahifaga o'tib bittagina bid yuborish."""
    page.goto(f"{APP_URL}/loads")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # "Be first" — broker hali bid yubormagan birinchi yuk
    page.get_by_text("Be first").first.click()
    page.wait_for_timeout(2500)

    # Bid form'ni ochish
    page.get_by_role("button", name="Place a bid").first.click()
    page.wait_for_timeout(2500)

    # Note kiritish
    page.get_by_placeholder("Why is your offer better than others?").fill(
        "Counter increment test bid"
    )
    page.wait_for_timeout(500)

    # Submit
    page.get_by_role("button", name="Place a bid").last.click()
    page.wait_for_timeout(5000)


@allure.feature("Usage Counter")
@allure.story("Bids placed counter increments by 1 after placing a bid")
@allure.severity(allure.severity_level.CRITICAL)
def test_bids_placed_counter_increments_by_one(logged_in_broker: Page):
    """
    Broker bid yuborganda 'Bids placed' counter aniq 1 ga ortadi.

    Stsenariy:
    1. Joriy 'Bids placed' qiymatini o'qish (N)
    2. Bittagina bid yuborish
    3. Yangi qiymat N+1 ekanligini tasdiqlash
    """
    page = logged_in_broker
    page.set_default_timeout(60000)

    initial_count = _read_bids_placed_count(page)
    _place_one_bid(page)
    new_count = _read_bids_placed_count(page)

    assert new_count == initial_count + 1, (
        f"Bids placed counter aniq 1 ga ortishi kerak edi: "
        f"avval={initial_count}, hozir={new_count}, kutilgan={initial_count + 1}"
    )
