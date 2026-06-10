from tests_mobile.screens.base_screen import BaseScreen


class LoginScreen(BaseScreen):
    TITLE_RU = "Авторизация"
    PASSWORD_HINT_RU = "Введите пароль"
    SUBMIT_RU = "Войти"
    FORGOT_PASSWORD_RU = "Забыли пароль?"
    REGISTER_RU = "Зарегистрироваться"

    def expect_visible(self):
        self.wait_for_text(self.TITLE_RU)
        self.wait_for_text(self.SUBMIT_RU)
        return self

    def login(self, email: str, password: str):
        self.expect_visible()

        edit_fields = self.device.find_nodes_by_class("android.widget.EditText")
        if len(edit_fields) < 2:
            raise AssertionError(
                f"Expected at least 2 input fields on login screen, found {len(edit_fields)}"
            )

        self.device.tap_node(edit_fields[0])
        self.device.text(email)
        self.device.tap_node(edit_fields[1])
        self.device.text(password)
        self.device.tap_text(self.SUBMIT_RU)
        self.device.wait(seconds=3)
        return self

    def open_forgot_password(self):
        self.expect_visible()
        self.device.tap_text(self.FORGOT_PASSWORD_RU)
        self.device.wait(seconds=1)
        return self

    def open_register(self):
        self.expect_visible()
        self.device.tap_text(self.REGISTER_RU)
        self.device.wait(seconds=1)
        return self
