from tests_mobile.screens.base_screen import BaseScreen


class ForgotPasswordScreen(BaseScreen):
    TITLE_RU = "Восстановление пароля"
    DESCRIPTION_RU = "Введите зарегистрированный адрес электронной почты или номер телефона"
    NEXT_RU = "Следующий"

    def expect_visible(self):
        self.wait_for_text(self.TITLE_RU)
        self.wait_for_text(self.DESCRIPTION_RU)
        self.wait_for_text(self.NEXT_RU)
        return self

    def submit_email_or_phone(self, value: str):
        self.expect_visible()
        edit_fields = self.device.find_nodes_by_class("android.widget.EditText")
        if not edit_fields:
            raise AssertionError("Expected email/phone input on forgot password screen")

        self.device.tap_node(edit_fields[0])
        self.device.text(value)
        self.device.tap_text(self.NEXT_RU)
        self.device.wait(seconds=2)
        return self
