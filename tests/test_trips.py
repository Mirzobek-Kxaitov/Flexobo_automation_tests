from playwright.sync_api import Page, expect

def test_add_trip(logged_in: Page):
    page = logged_in
    page.goto("https://app.flexobo-mock.site/trips/create")
    accept_button = page.get_by_role("button", name="Accept")
    if accept_button.is_visible():
        accept_button.click()

    # Step 1 - Transport
    page.get_by_role("combobox").first.click()
    page.get_by_role("option", name="Trailer 1").click()
    page.get_by_role("combobox").filter(has_text="Choose").click()
    page.get_by_text("kg").click()
    page.get_by_role("textbox", name="Volume*").fill("10")
    page.get_by_role("textbox", name="Loading", exact=True).fill("tashkent")
    page.get_by_text("Tashkent").first.click()
    page.get_by_role("textbox", name="Loading radius", exact=True).fill("12")
    page.get_by_role("textbox", name="Unloading", exact=True).fill("denov")
    page.get_by_text("Denov District", exact=True).click()
    page.get_by_role("textbox", name="Unloading radius").fill("12")
    page.get_by_role("button", name="Next").click()

    # Step 2 - Price
    page.get_by_role("textbox", name="Price*").fill("1200")
    page.get_by_role("button", name="Next").click()

    # Step 3 - Transport tab
    page.get_by_role("tab", name="Transport").click()

    # Trips ro'yxat sahifasiga o'tish
    page.goto("https://app.flexobo-mock.site/trips")

    # Assert - yangi trip yaratilganini tekshirish
    expect(page.get_by_text("USD 1,200").first).to_be_visible()
    expect(page.get_by_text("Tashkent").first).to_be_visible()
    expect(page.get_by_text("Trailer 1").first).to_be_visible()
    expect(page.get_by_text("New").first).to_be_visible()
