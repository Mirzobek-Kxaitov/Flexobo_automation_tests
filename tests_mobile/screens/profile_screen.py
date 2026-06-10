from tests_mobile.screens.base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    PROFILE_TITLE_RU = "Профиль"
    LOGOUT_RU = "Выйти"

    # Bottom navigation icons currently have no labels in the Flutter semantics tree.
    PROFILE_TAB_X = 978
    PROFILE_TAB_Y = 2214

    def open_from_bottom_nav(self):
        self.device.tap(self.PROFILE_TAB_X, self.PROFILE_TAB_Y)
        self.device.wait(seconds=1)
        return self

    def expect_visible(self):
        self.wait_for_text(self.PROFILE_TITLE_RU)
        return self

    def logout(self):
        self.expect_visible()
        self.device.scroll_until_text(self.LOGOUT_RU, max_swipes=5)
        self.device.tap_text(self.LOGOUT_RU)
        self.device.wait(seconds=1)
        self.device.tap_first_visible_text(["Да", "Yes", "Выйти"])
        self.device.wait(seconds=2)
        return self
