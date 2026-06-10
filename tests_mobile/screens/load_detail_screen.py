from tests_mobile.screens.base_screen import BaseScreen


class LoadDetailScreen(BaseScreen):
    def expect_visible_for_load(self, load_summary: str):
        summary_lines = [line.strip() for line in load_summary.splitlines() if line.strip()]
        if not summary_lines:
            raise AssertionError("Load summary is empty")

        self.wait_for_text(summary_lines[0], timeout=15)
        return self
