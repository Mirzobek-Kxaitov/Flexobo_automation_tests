from tests_mobile.utils.adb import AdbDevice


class BaseScreen:
    def __init__(self, device: AdbDevice):
        self.device = device

    def dump(self):
        return self.device.dump_ui()

    def wait_for_text(self, text: str, timeout: float = 10):
        self.device.wait_for_text(text, timeout=timeout)
        return self

    def wait_for_any_text(self, texts: list[str], timeout: float = 10):
        self.device.wait_for_any_text(texts, timeout=timeout)
        return self
