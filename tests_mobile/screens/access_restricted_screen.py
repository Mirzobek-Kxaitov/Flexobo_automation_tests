from tests_mobile.screens.base_screen import BaseScreen


class AccessRestrictedScreen(BaseScreen):
    TITLE_RU = "У вас нет доступа к этому приложению"
    MESSAGE_RU = "Для вашей роли это приложение пока недоступно"
    LOGOUT_RU = "Выйти"

    def expect_visible(self):
        self.wait_for_text(self.TITLE_RU, timeout=20)
        self.wait_for_text(self.MESSAGE_RU)
        self.wait_for_text(self.LOGOUT_RU)
        return self
