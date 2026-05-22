import time
import allure
import pytest
from playwright.sync_api import Page
from pages.fleet_page import FleetPage


# Fleet sahifasiga kirish mumkin bo'lgan rollar
FLEET_CAPABLE_ROLES = ["broker", "carrier", "owner_operator"]

# Owner Operator da Trucks tab yo'q — faqat Trailers
TRUCK_CAPABLE_ROLES = ["broker", "carrier"]


# ── Truck tests ─────────────────────────────────────────────────


@allure.feature("Fleet")
@allure.story("Create truck")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", TRUCK_CAPABLE_ROLES)
def test_create_truck(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    FleetPage(page).create_truck(
        country="Uzbekistan",
        country_search="uzb",
        gov_number="TEST-TRUCK-01",
        brand="KAMAZ",
        year="2016",
        lifting_capacity="tons",
        technical_passport="12345678",
    ).expect_on_fleet_page().expect_truck_in_list("KAMAZ", "TEST-TRUCK-01")


@allure.feature("Fleet")
@allure.story("Edit truck")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", TRUCK_CAPABLE_ROLES)
def test_edit_truck(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    fleet = FleetPage(page)

    fleet.create_truck(
        country="Uzbekistan",
        country_search="uzb",
        gov_number="TEST-TRUCK-EDIT",
        brand="KAMAZ",
        year="2016",
    )

    fleet.edit_truck(
        brand="KAMAZ",
        gov_number="TEST-TRUCK-EDIT",
        new_brand="HYUNDAI",
    ).expect_truck_updated()


@allure.feature("Fleet")
@allure.story("Delete truck")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", TRUCK_CAPABLE_ROLES)
def test_delete_truck(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    fleet = FleetPage(page)
    gov = f"DEL-{int(time.time())}"

    fleet.create_truck(
        country="Uzbekistan",
        country_search="uzb",
        gov_number=gov,
        brand="KAMAZ",
        year="2016",
    ).expect_truck_in_list("KAMAZ", gov)

    fleet.delete_truck("KAMAZ", gov).expect_truck_deleted()


# ── Trailer tests ───────────────────────────────────────────────


@allure.feature("Fleet")
@allure.story("Create trailer")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", FLEET_CAPABLE_ROLES)
def test_create_trailer(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    FleetPage(page).create_trailer(
        country="United Arab Emirates",
        gov_number="TEST-TRL-01",
        trailer_type="Trailer 1",
        year="2018",
        lifting_capacity="tons",
        volume=10,
        length=12,
        width=3,
        height=3,
    ).expect_on_fleet_page().expect_trailer_in_list("TEST-TRL-01")


@allure.feature("Fleet")
@allure.story("Edit trailer")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", FLEET_CAPABLE_ROLES)
def test_edit_trailer(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    fleet = FleetPage(page)

    fleet.create_trailer(
        country="United Arab Emirates",
        gov_number="TEST-TRL-EDIT",
        trailer_type="Trailer 1",
        year="2018",
    )

    fleet.edit_trailer(
        gov_number="TEST-TRL-EDIT",
        new_gov_number="TEST-TRL-EDITED",
    ).expect_on_fleet_page().expect_trailer_in_list("TEST-TRL-EDITED")


@allure.feature("Fleet")
@allure.story("Deactivate and reactivate trailer")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("role", FLEET_CAPABLE_ROLES)
def test_deactivate_and_reactivate_trailer(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    fleet = FleetPage(page)

    fleet.create_trailer(
        country="United Arab Emirates",
        gov_number="TEST-TRL-DEACT",
        trailer_type="Trailer 1",
        year="2018",
    )

    fleet.deactivate_trailer("TEST-TRL-DEACT").expect_on_fleet_page()
    fleet.reactivate_trailer("TEST-TRL-DEACT").expect_on_fleet_page()


@allure.feature("Fleet")
@allure.story("Delete trailer")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("role", FLEET_CAPABLE_ROLES)
def test_delete_trailer(request, role: str):
    page: Page = request.getfixturevalue(f"logged_in_{role}")
    fleet = FleetPage(page)

    fleet.create_trailer(
        country="United Arab Emirates",
        gov_number="TEST-TRL-DEL",
        trailer_type="Trailer 1",
        year="2018",
    )

    # Trailer must be deactivated before deletion
    fleet.deactivate_trailer("TEST-TRL-DEL")
    fleet.delete_trailer("TEST-TRL-DEL").expect_trailer_deleted()
