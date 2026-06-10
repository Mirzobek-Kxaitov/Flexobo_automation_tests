from tests_mobile.screens.base_screen import BaseScreen


class HomeScreen(BaseScreen):
    # These labels are enough for a role-agnostic smoke check after login.
    KNOWN_HOME_TEXTS_RU = [
        "Грузы",
        "Грузовики",
        "Профиль",
        "Мои объявления",
        "Фильтр",
    ]

    def expect_logged_in(self):
        self.wait_for_any_text(self.KNOWN_HOME_TEXTS_RU, timeout=20)
        return self
