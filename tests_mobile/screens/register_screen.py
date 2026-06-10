from tests_mobile.screens.base_screen import BaseScreen


class RegisterScreen(BaseScreen):
    TITLE_RU = "Регистрация"
    DESCRIPTION_RU = "Создайте аккаунт"
    NEXT_RU = "Следующий"

    def expect_visible(self):
        self.wait_for_text(self.TITLE_RU)
        self.wait_for_text(self.DESCRIPTION_RU)
        self.wait_for_text(self.NEXT_RU)
        return self
